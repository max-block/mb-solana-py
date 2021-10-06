import click

from mb_solana import solana_account
from mb_solana.cli.helpers import print_json


@click.command(name="generate-accounts", help="Generate new accounts")
@click.option("--limit", "-l", type=int, default=5)
@click.option("--array", is_flag=True, help="Print private key in the array format.")
def cli(limit: int, array: bool):
    result = {}
    for _ in range(limit):
        acc = solana_account.generate_account()
        private_key = acc.private_key_base58
        if array:
            private_key = solana_account.get_private_key_arr_str(acc.private_key_base58)
        result[acc.public_key] = private_key
    print_json(result)
