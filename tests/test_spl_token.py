from mb_solana import spl_token


def test_get_balance(mainnet_node, usdt_token_address, usdt_owner_address):
    res = spl_token.get_balance(mainnet_node, usdt_owner_address, usdt_token_address)
    assert res.ok > 0
