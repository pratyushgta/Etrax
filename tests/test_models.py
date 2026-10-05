from datetime import date
from decimal import Decimal

import pytest

from src.etrax.processing.models import NormalizedTransaction


def test_valid_expense():
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Grocery Store",
        debit=Decimal("500.00")
    )

    assert transaction.debit == Decimal("500.00")
    assert transaction.credit == Decimal("0")


def test_valid_income():
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Salary",
        credit=Decimal("70000.00")
    )

    assert transaction.credit == Decimal("70000.00")
    assert transaction.debit == Decimal("0")


def test_negative_debit_rejected():
    with pytest.raises(ValueError):
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Invalid",
            debit=Decimal("-100")
        )


def test_negative_credit_rejected():
    with pytest.raises(ValueError):
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Invalid",
            credit=Decimal("-100")
        )


def test_debit_and_credit_rejected():
    with pytest.raises(ValueError):
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Invalid",
            debit=Decimal("100"),
            credit=Decimal("100")
        )


def test_empty_description_rejected():
    with pytest.raises(ValueError):
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="   ",
            debit=Decimal("100")
        )


def test_balance_supported():
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Grocery Store",
        debit=Decimal("500"),
        balance=Decimal("9500")
    )

    assert transaction.balance == Decimal("9500")