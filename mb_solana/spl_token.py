from decimal import Decimal
from typing import Optional

from mb_commons import Result
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts


def get_balance(node: str, owner_address: str, token_mint_address: str, token_account: Optional[str] = None) -> Result[Decimal]:
    try:
        client = Client(endpoint=node)
        if not token_account:
            res = client.get_token_accounts_by_owner(
                PublicKey(owner_address),
                TokenAccountOpts(mint=PublicKey(token_mint_address)),
            )
            if not res["result"]["value"]:
                return Result(error="no_token_accounts")

            token_accounts = [PublicKey(a["pubkey"]) for a in res["result"]["value"]]
            balances = []
            for token_account in token_accounts:
                res = client.get_token_account_balance(token_account)
                balance = Decimal(res["result"]["value"]["amount"])
                if balance:
                    balances.append(balance)

            if len(balances) > 1:
                return Result(error="there are many non empty token accounts, set token_account explicitly")
            return Result(ok=balances[0])

        res = client.get_token_account_balance(token_account)
        return Result(ok=Decimal(res["result"]["value"]["amount"]))
    except Exception as e:
        return Result(error="exception", data=str(e))
