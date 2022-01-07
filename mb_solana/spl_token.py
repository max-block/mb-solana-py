from decimal import Decimal

from mb_std import Result
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.core import RPCException
from solana.rpc.types import TokenAccountOpts
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID

from mb_solana import solana_account


def get_balance(node: str, owner_address: str, token_mint_address: str, token_account: str | None = None) -> Result[Decimal]:
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


def transfer_to_wallet_address(
    *,
    node: str,
    private_key: str,
    recipient_wallet_address: str,
    token_mint_address: str,
    amount: int,
) -> Result[str]:
    try:
        keypair = solana_account.get_keypair(private_key)
        token_client = Token(Client(node), PublicKey(token_mint_address), program_id=TOKEN_PROGRAM_ID, payer=keypair)

        # get from_token_account
        res = token_client.get_accounts(keypair.public_key)
        token_accounts = res["result"]["value"]
        if len(token_accounts) > 1:
            return Result(error="many_from_token_accounts", data=res)
        from_token_account = PublicKey(token_accounts[0]["pubkey"])

        # get to_token_account
        res = token_client.get_accounts(PublicKey(recipient_wallet_address))
        token_accounts = res["result"]["value"]
        if len(token_accounts) > 1:
            return Result(error="many_to_token_accounts", data=res)
        elif len(token_accounts) == 1:
            to_token_account = PublicKey(token_accounts[0]["pubkey"])
        else:  # create a new to_token_account
            to_token_account = token_client.create_account(owner=PublicKey(recipient_wallet_address))

        res = token_client.transfer(source=from_token_account, dest=to_token_account, owner=keypair, amount=amount)
        if res.get("result"):
            return Result(ok=res.get("result"), data=res)
        return Result(error="unknown_response", data=res)
    except RPCException as e:
        return Result(error="rcp_exception", data=str(e))
    except Exception as e:
        return Result(error="exception", data=str(e))
