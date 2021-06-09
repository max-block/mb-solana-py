import random
from decimal import Decimal

import click
from mb_commons import str_to_list
from pydantic import StrictStr, validator

from mb_solana import helpers
from mb_solana.cli.helpers import BaseCmdConfig, parse_config, print_config_and_exit, print_json


class Config(BaseCmdConfig):
    from_address: StrictStr
    private_key: StrictStr
    recipients: list[StrictStr]
    nodes: list[StrictStr]
    amount: Decimal

    @validator("recipients", "nodes", pre=True)
    def to_list_validator(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return str_to_list(v, unique=True, remove_comments=True)
        return v

    @property
    def random_node(self) -> str:
        return random.choice(self.nodes)


@click.command(name="transfer-sol", help="Transfer SOL")
@click.argument("config_path", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config_path):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)
    result = {}
    for recipient in config.recipients:
        res = helpers.transfer_sol(
            from_address=config.from_address,
            private_key_base58=config.private_key,
            recipient_address=recipient,
            amount_sol=config.amount,
            nodes=config.nodes,
        )
        result[recipient] = res.ok_or_error
    print_json(result)
