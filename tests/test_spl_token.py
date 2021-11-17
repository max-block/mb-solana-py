from mb_solana import solana_account, spl_token


def test_get_balance(mainnet_node, usdt_token_address, usdt_owner_address):
    # existing token account
    res = spl_token.get_balance(mainnet_node, usdt_owner_address, usdt_token_address)
    assert res.ok > 0

    res = spl_token.get_balance(mainnet_node, solana_account.generate_account().public_key, usdt_token_address)
    assert res.error == "no_token_accounts"
