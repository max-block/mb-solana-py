import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def mainnet_node():
    return os.getenv("MAINNET_NODE")


@pytest.fixture
def usdt_token_address():
    return os.getenv("USDT_TOKEN_ADDRESS")


@pytest.fixture
def usdt_owner_address():
    return os.getenv("USDT_OWNER_ADDRESS")
