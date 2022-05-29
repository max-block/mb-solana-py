import random
from decimal import Decimal

import pydash
from mb_std import Result
from pydantic import BaseModel
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction

from mb_solana import solana_rpc
from mb_solana.solana_account import get_keypair


def transfer_sol(
    *,
    from_address: str,
    private_key_base58: str,
    recipient_address: str,
    amount_sol: Decimal,
    node: str | None = None,
    nodes: list[str] | None = None,
    attempts=3,
) -> Result[str]:
    if not node and not nodes:
        raise ValueError("node or nodes must be set")

    acc = get_keypair(private_key_base58)
    if acc.public_key != PublicKey(from_address):
        raise ValueError("from_address or private_key_base58 is invalid")

    lamports = int(amount_sol * 10**9)
    error = None
    data = None
    for _ in range(attempts):
        try:
            client = Client(node or random.choice(nodes))  # type:ignore
            tx = Transaction(fee_payer=acc.public_key)
            ti = transfer(
                TransferParams(from_pubkey=acc.public_key, to_pubkey=PublicKey(recipient_address), lamports=lamports),
            )
            tx.add(ti)
            res = client.send_transaction(tx, acc)
            data = res
            tx = data.get("result")
            if tx and isinstance(tx, str):
                return Result(ok=tx, data=data)
        except Exception as e:
            error = str(e)

    return Result(error=error, data=data)


def lamports_to_sol(lamports: int, ndigits=4) -> Decimal:
    return Decimal(str(round(lamports / 10**9, ndigits=ndigits)))


class TransferInfo(BaseModel):
    source: str
    destination: str
    lamports: int


def find_transfers(node: str, tx_signature: str) -> Result[list[TransferInfo]]:
    res = solana_rpc.get_transaction(node, tx_signature, encoding="jsonParsed")
    if res.is_error():
        return res  # type:ignore
    result = []
    try:
        for ix in pydash.get(res.ok, "transaction.message.instructions"):
            program_id = ix.get("programId")
            ix_type = pydash.get(ix, "parsed.type")
            if program_id == "11111111111111111111111111111111" and ix_type == "transfer":
                source = pydash.get(ix, "parsed.info.source")
                destination = pydash.get(ix, "parsed.info.destination")
                lamports = pydash.get(ix, "parsed.info.lamports")
                if source and destination and lamports:
                    result.append(TransferInfo(source=source, destination=destination, lamports=lamports))
        return Result.new_ok(result, res.dict())
    except Exception as e:
        return Result.new_error("exception", {"error": str(e), "response": res.dict()})
