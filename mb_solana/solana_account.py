import random
from typing import Optional, Union

import base58
import pydash
from mb_commons import Result
from nacl.public import PrivateKey
from pydantic import BaseModel
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client


class NewAccount(BaseModel):
    public_key: str
    private_key_base58: str
    private_key_arr: list[int]


def generate_account() -> NewAccount:
    keypair = Keypair.generate()
    public_key = keypair.public_key.to_base58().decode("utf-8")
    private_key_base58 = base58.b58encode(keypair.secret_key).decode()
    private_key_arr = [x for x in keypair.secret_key]  # noqa
    return NewAccount(public_key=public_key, private_key_base58=private_key_base58, private_key_arr=private_key_arr)


def get_keypair(private_key: Union[str, list[int]]) -> Keypair:
    if isinstance(private_key, str):
        if "[" in private_key:
            private_key_ = [int(x) for x in private_key.replace("[", "").replace("]", "").split(",")]
        else:
            private_key_ = base58.b58decode(private_key)
    else:
        private_key_ = private_key
    return Keypair(PrivateKey(bytes(private_key_[:32])))


def check_private_key(public_key_base58: str, private_key: Union[str, list[int]]) -> bool:
    return get_keypair(private_key).public_key.to_base58().decode("utf-8") == public_key_base58


def get_public_key(private_key: str) -> str:
    if "[" in private_key:
        private_key_ = [int(x) for x in private_key.replace("[", "").replace("]", "").split(",")]
    else:
        private_key_ = base58.b58decode(private_key)
    return Keypair(PrivateKey(bytes(private_key_[:32]))).public_key.to_base58().decode()


def get_private_key_base58(private_key: str) -> str:
    keypair = get_keypair(private_key)
    return base58.b58encode(keypair.secret_key).decode()


def get_private_key_arr(private_key: str) -> list[int]:
    keypair = get_keypair(private_key)
    return list(x for x in keypair.secret_key)  # noqa


def get_private_key_arr_str(private_key: str) -> str:
    return f"[{','.join(str(x) for x in get_private_key_arr(private_key))}]"


def is_empty_account(
    *,
    address: str,
    node: Optional[str] = None,
    nodes: Optional[list[str]] = None,
    attempts=3,
) -> Result[bool]:
    if not node and not nodes:
        raise ValueError("node or nodes must be set")
    error = None
    data = None
    for _ in range(attempts):
        try:
            client = Client(node or random.choice(nodes))  # type:ignore
            res = client.get_account_info(PublicKey(address))
            data = res
            slot = pydash.get(res, "result.context.slot")
            value = pydash.get(res, "result.value")
            if slot and value is None:
                return Result(ok=True, data=data)
            if slot and value:
                return Result(ok=False, data=data)
        except Exception as e:
            error = str(e)
    return Result(error=error or "unknown response", data=data)
