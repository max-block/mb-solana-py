import random
from decimal import Decimal
from typing import Optional

import base58
from mb_commons import Result
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction


def transfer_sol(
    *,
    from_address: str,
    private_key_base58: str,
    recipient_address: str,
    amount_sol: Decimal,
    node: Optional[str] = None,
    nodes: Optional[list[str]] = None,
    attempts=3,
) -> Result[str]:
    if not node and not nodes:
        raise ValueError("node or nodes must be set")
    acc = Account(base58.b58decode(private_key_base58)[:32])
    if str(acc.public_key()) != from_address:
        raise ValueError("from_address or private_key_base58 is invalid")

    lamports = int(amount_sol * 10 ** 9)
    error = None
    data = None
    for _ in range(attempts):
        try:
            client = Client(node or random.choice(nodes))  # type:ignore
            tx = Transaction(fee_payer=acc.public_key())
            ti = transfer(
                TransferParams(from_pubkey=acc.public_key(), to_pubkey=PublicKey(recipient_address), lamports=lamports),
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
