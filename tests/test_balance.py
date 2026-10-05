from decimal import Decimal

from src.etrax.processing.balance import (
    VALIDATION_VALID,
    VALIDATION_MISMATCH,
    VALIDATION_INCOMPLETE,
    calculate_closing_balance,
    validate_balance
)


def test_calculate_closing_balance():
    result = calculate_closing_balance(
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000
    )

    assert result == Decimal("58000")


def test_valid_balance():
    result = validate_balance(
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        statement_closing_balance=58000
    )

    assert result["validation_status"] == VALIDATION_VALID
    assert result["calculated_closing"] == Decimal("58000")
    assert result["difference"] == Decimal("0")


def test_mismatched_balance():
    result = validate_balance(
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        statement_closing_balance=57500
    )

    assert result["validation_status"] == VALIDATION_MISMATCH
    assert result["calculated_closing"] == Decimal("58000")
    assert result["difference"] == Decimal("500")


def test_small_rounding_difference_is_valid():
    result = validate_balance(
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        statement_closing_balance=58000.01
    )

    assert result["validation_status"] == VALIDATION_VALID


def test_missing_balance_is_incomplete():
    result = validate_balance(
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        statement_closing_balance=None
    )

    assert result["validation_status"] == VALIDATION_INCOMPLETE
    assert result["calculated_closing"] is None
    assert result["difference"] is None