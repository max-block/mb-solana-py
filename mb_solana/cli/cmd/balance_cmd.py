import random

import click
import pydash
from mb_std import str_to_list
from pydantic import StrictStr, validator
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts

from mb_solana.cli.helpers import BaseCmdConfig, parse_config, print_config_and_exit, print_json


class Config(BaseCmdConfig):
    accounts: list[StrictStr]
    nodes: list[StrictStr]
    tokens: list[StrictStr] | None = None

    @validator("accounts", "nodes", "tokens", pre=True)
    def to_list_validator(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return str_to_list(v, unique=True, remove_comments=True)
        return v

    @property
    def random_node(self) -> str:
        return random.choice(self.nodes)


@click.command(name="balance", help="Print SOL and tokens balances")
@click.argument("config_path", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config_path):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)
    result = {"sol": _get_sol_balances(config.accounts, config.nodes)}

    if config.tokens:
        for token in config.tokens:
            result[token] = _get_token_balances(token, config.accounts, config.nodes)

    print_json(result)


def _get_token_balances(token: str, accounts: list[str], nodes: list[str]) -> dict[str, float | None]:
    result = {}
    for account in accounts:
        result[account] = _get_token_balance(token, account, nodes)
    return result


def _get_token_balance(token: str, account: str, nodes: list[str]) -> float | None:
    for _ in range(3):
        client = Client(random.choice(nodes))
        res = client.get_token_accounts_by_owner(PublicKey(account), TokenAccountOpts(mint=PublicKey(token)))
        token_account = pydash.get(res, "result.value.0.pubkey")
        if token_account:
            res = client.get_token_account_balance(token_account)
            return pydash.get(res, "result.value.uiAmount")


def _get_sol_balances(accounts: list[str], nodes: list[str]) -> dict[str, float | None]:
    result = {}
    for account in accounts:
        result[account] = _get_balance(account, nodes)
    return result


def _get_balance(account: str, nodes: list[str]) -> float | None:
    for _ in range(3):
        client = Client(random.choice(nodes))
        value = pydash.get(client.get_balance(account), "result.value")
        if value:
            return value / 10**9
