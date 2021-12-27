import click
from mb_std import md

from mb_solana import solana_account
from mb_solana.cli.helpers import print_json


@click.command(name="keypair", help="Print public, private_base58, private_arr by a private key")
@click.argument("private_key")
def cli(private_key: str):
    public = solana_account.get_public_key(private_key)
    private_base58 = solana_account.get_private_key_base58(private_key)
    private_arr = solana_account.get_private_key_arr_str(private_key)
    print_json(md(public, private_base58, private_arr))
