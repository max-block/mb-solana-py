import json
import os
import random
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Optional, Union

import pydash
from mb_commons import Result, md, shell
from mb_commons.shell import CommandResult
from pydantic import BaseModel, Field, validator


@dataclass
class ValidatorInfo:
    identity_address: str
    info_address: str
    name: Optional[str]
    keybase: Optional[str]
    website: Optional[str]
    details: Optional[str]


class BlockProduction(BaseModel):
    class Leader(BaseModel):
        validator: str = Field(..., alias="identityPubkey")
        leader: int = Field(..., alias="leaderSlots")
        produced: int = Field(..., alias="blocksProduced")
        skipped: int = Field(..., alias="skippedSlots")

        class Config:
            allow_population_by_field_name = True

    epoch: int
    start_slot: int
    end_slot: int
    leaders: list[Leader]


class StakeAccount(BaseModel):
    type: str = Field(..., alias="stakeType")
    balance: float = Field(..., alias="accountBalance")
    withdrawer: str
    staker: str
    vote: Optional[str] = Field(None, alias="delegatedVoteAccountAddress")

    @validator("balance")
    def from_lamports_to_sol(cls, v):
        if v:
            return v / 1_000_000_000


class Stake(BaseModel):
    stake_address: str = Field(..., alias="stakePubkey")
    withdrawer_address: str = Field(..., alias="withdrawer")
    vote_address: Optional[str] = Field(None, alias="delegatedVoteAccountAddress")
    balance: float = Field(..., alias="accountBalance")
    delegated: Optional[float] = Field(None, alias="delegatedStake")
    active: Optional[float] = Field(None, alias="activeStake")
    lock_time: Optional[int] = Field(None, alias="unixTimestamp")

    @validator("balance", "delegated", "active")
    def from_lamports_to_sol(cls, v):
        if v:
            return v / 1_000_000_000

    class Config:
        allow_population_by_field_name = True


def get_balance(
    *,
    address: str,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[Decimal]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana balance {address} -u {url}"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        return Result(ok=Decimal(res.stdout.replace("SOL", "").strip()), data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def get_slot(
    *,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[int]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana slot -u {url}"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        return Result(ok=int(res.stdout), data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def get_stake_account(
    *,
    address: str,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[StakeAccount]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana stake-account --output json -u {url} {address}"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        json_res = json.loads(res.stdout)
        return Result(ok=StakeAccount(**json_res), data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


# noinspection DuplicatedCode
def transfer_with_private_key_file(
    *,
    recipient: str,
    amount: Decimal,
    private_key_path: str,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    allow_unfunded_recipient=True,
    timeout=60,
) -> Result[str]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana transfer {recipient} {amount} --from {private_key_path} --fee-payer {private_key_path}"
    if allow_unfunded_recipient:
        cmd += " --allow-unfunded-recipient"
    cmd += f" -u {url} --output json"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        json_res = json.loads(res.stdout)
        return Result(ok=json_res["signature"], data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def transfer_with_private_key_str(
    *,
    recipient: str,
    amount: Decimal,
    private_key: str,
    tmp_dir_path: str,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[str]:
    # make private_key file
    private_key_path = f"{tmp_dir_path}/solana__{random.randint(1, 10_000_000_000)}.json"
    with open(private_key_path, "w") as f:
        f.write(private_key)

    try:
        return transfer_with_private_key_file(
            recipient=recipient,
            amount=amount,
            private_key_path=private_key_path,
            solana_dir=solana_dir,
            url=url,
            ssh_host=ssh_host,
            ssh_key_path=ssh_key_path,
            timeout=timeout,
        )
    finally:
        os.remove(private_key_path)


def withdraw_from_vote_account(
    *,
    recipient: str,
    amount: Union[Decimal, Literal["ALL"]],
    vote_key_path: str,
    fee_payer_key_path: str,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[str]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana withdraw-from-vote-account --keypair {fee_payer_key_path} -u {url} --output json {vote_key_path} {recipient} {amount}"  # noqa
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        json_res = json.loads(res.stdout)
        return Result(ok=json_res["signature"], data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def get_validators_info(
    *,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[list[ValidatorInfo]]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana validator-info get --output json -u {url}"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        validators = []
        for v in json.loads(res.stdout):
            validators.append(
                ValidatorInfo(
                    info_address=v["infoPubkey"],
                    identity_address=v["identityPubkey"],
                    name=pydash.get(v, "info.name"),
                    keybase=pydash.get(v, "info.keybaseUsername"),
                    details=pydash.get(v, "info.details"),
                    website=pydash.get(v, "info.website"),
                ),
            )
        return Result(ok=validators, data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def get_vote_account_rewards(
    *,
    address: str,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    num_rewards_epochs=10,
    timeout=60,
) -> Result[dict[int, float]]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana vote-account {address} --with-rewards --num-rewards-epochs={num_rewards_epochs} -u {url}"
    cmd += " --output json 2>/dev/null"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = md(cmd, res.stdout, res.stderr)
    try:
        rewards: dict[int, float] = {}
        for r in reversed(json.loads(res.stdout)["epochRewards"]):
            rewards[r["epoch"]] = r["amount"] / 10 ** 9
        return Result(ok=rewards, data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def get_block_production(
    *,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[BlockProduction]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana block-production --output json -u {url}"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    try:
        stdout = res.stdout.strip()
        data = {"stdout": res.stdout, "stderr": res.stderr}
        if stdout.startswith("Note:") and "\n" in stdout:
            data["note"] = stdout[: stdout.index("\n")]
            stdout = stdout[stdout.index("\n") + 1 :]  # noqa
        return Result(ok=BlockProduction(**json.loads(stdout)), data=data)
    except Exception as e:
        return Result(error=str(e), data={"stdout": res.stdout, "stderr": res.stderr})


def get_stakes(
    *,
    solana_dir="",
    url="localhost",
    ssh_host: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
    timeout=60,
) -> Result[list[Stake]]:
    solana_dir = _solana_dir(solana_dir)
    cmd = f"{solana_dir}solana stakes --output json -u {url}"
    res = _exec_cmd(cmd, ssh_host, ssh_key_path, timeout)
    data = {"stdout": res.stdout, "stderr": res.stderr}
    try:
        return Result(ok=[Stake(**x) for x in json.loads(res.stdout)], data=data)
    except Exception as e:
        return Result(error=str(e), data=data)


def _exec_cmd(cmd: str, ssh_host: Optional[str], ssh_key_path: Optional[str], timeout: int) -> CommandResult:
    if ssh_host:
        return shell.run_ssh_command(ssh_host, cmd, ssh_key_path, timeout=timeout)
    return shell.run_command(cmd, timeout=timeout)


def _solana_dir(solana_dir: str) -> str:
    if solana_dir and not solana_dir.endswith("/"):
        solana_dir += "/"
    return solana_dir


if __name__ == "__main__":
    pass
