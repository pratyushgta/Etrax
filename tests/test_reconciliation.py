from datetime import date
from decimal import Decimal

from src.etrax.processing.models import NormalizedTransaction
from src.etrax.processing.reconciliation import (
    reconcile_statement
)


def test_valid_statement():
    transactions = [
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Salary",
            credit=Decimal("70000")
        ),
        NormalizedTransaction(
            transaction_date=date(2026, 10, 2),
            description="Groceries",
            debit=Decimal("4000")
        ),
        NormalizedTransaction(
            transaction_date=date(2026, 10, 3),
            description="Shopping",
            debit=Decimal("3000")
        )
    ]

    result = reconcile_statement(
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=73000
    )

    assert result["validation_status"] == "VALID"
    assert result["total_credits"] == Decimal("70000")
    assert result["total_debits"] == Decimal("7000")
    assert result["calculated_closing_balance"] == Decimal("73000")
    assert result["difference"] == Decimal("0")
    assert result["transaction_count"] == 3


def test_mismatched_statement():
    transactions = [
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Salary",
            credit=Decimal("70000")
        ),
        NormalizedTransaction(
            transaction_date=date(2026, 10, 2),
            description="Groceries",
            debit=Decimal("4000")
        )
    ]

    result = reconcile_statement(
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=75000
    )

    assert result["validation_status"] == "MISMATCH"
    assert result["calculated_closing_balance"] == Decimal("76000")
    assert result["difference"] == Decimal("1000")


def test_incomplete_statement():
    transactions = [
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Salary",
            credit=Decimal("70000")
        )
    ]

    result = reconcile_statement(
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=None
    )

    assert result["validation_status"] == "INCOMPLETE"
    assert result["calculated_closing_balance"] is None
    assert result["difference"] is None


def test_multiple_transactions():
    transactions = [
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Salary",
            credit=Decimal("70000")
        ),
        NormalizedTransaction(
            transaction_date=date(2026, 10, 2),
            description="Groceries",
            debit=Decimal("4000")
        ),
        NormalizedTransaction(
            transaction_date=date(2026, 10, 3),
            description="Dining",
            debit=Decimal("2000")
        ),
        NormalizedTransaction(
            transaction_date=date(2026, 10, 4),
            description="Refund",
            credit=Decimal("500")
        )
    ]

    result = reconcile_statement(
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=74500
    )

    assert result["validation_status"] == "VALID"
    assert result["total_credits"] == Decimal("70500")
    assert result["total_debits"] == Decimal("6000")
    assert result["calculated_closing_balance"] == Decimal("74500")