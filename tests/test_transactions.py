import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.etrax.database.transactions import (
    get_transaction,
    list_transactions,
    total_spending
)


def test_transactions_exist():
    transactions = list_transactions()

    assert len(transactions) == 7


def test_salary_transaction_exists():
    transactions = list_transactions(account_id=2)

    salary = [
        transaction
        for transaction in transactions
        if transaction["transaction_type"] == "INCOME"
    ]

    assert len(salary) == 1
    assert salary[0]["credit"] == 70000


def test_transaction_lookup():
    transaction = get_transaction(1)

    assert transaction is not None
    assert transaction["account_id"] == 2
    assert transaction["description"] == "Salary Credit"


def test_total_spending():
    spending = total_spending()

    assert spending == 9000