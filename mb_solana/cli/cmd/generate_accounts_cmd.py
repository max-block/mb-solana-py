import click
from solana.account import Account

from mb_solana.cli.helpers import print_json


@click.command(name="generate-accounts", help="Generate new accounts")
@click.option("--limit", "-l", type=int, default=5)
def cli(limit: int):
    result = {}
    for _ in range(limit):
        acc = Account()
        public_key = acc.public_key().to_base58().decode("utf-8")
        private_key = acc.keypair().decode()
        result[public_key] = private_key
    print_json(result)
