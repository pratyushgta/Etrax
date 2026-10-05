import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.etrax.database.accounts import (
    list_accounts,
    get_account
)


def test_four_accounts_exist():
    accounts = list_accounts()
    assert len(accounts) == 4


def test_axis_liberty_exists():
    accounts = list_accounts()

    names = [
        account["account_name"]
        for account in accounts
    ]

    assert "Axis Liberty" in names


def test_idbi_exists():
    accounts = list_accounts()

    names = [
        account["account_name"]
        for account in accounts
    ]

    assert "IDBI Savings" in names


def test_get_account():
    account = get_account(2)

    assert account is not None
    assert account["account_name"] == "Axis Liberty"
    assert account["bank_name"] == "Axis Bank"