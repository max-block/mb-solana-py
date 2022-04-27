from decimal import Decimal

from mb_solana.helpers import lamports_to_sol


def test_lamports_to_sol():
    res = lamports_to_sol(272356343007, ndigits=4)
    assert res == Decimal("272.3563")
