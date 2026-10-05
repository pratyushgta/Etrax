from datetime import date
from decimal import Decimal

from src.etrax.processing.models import NormalizedTransaction
from src.etrax.processing.processor import process_transaction
from src.etrax.database.transactions import list_transactions


def test_process_expense(test_database):
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Grocery Store",
        debit=Decimal("500.00"),
        balance=Decimal("9500.00")
    )

    result = process_transaction(
        account_id=1,
        transaction=transaction,
        transaction_type="EXPENSE",
        category="Groceries",
        database_path=test_database
    )

    assert result["status"] == "CREATED"
    assert result["transaction_id"] == 1


def test_process_income(test_database):
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Salary",
        credit=Decimal("70000.00"),
        balance=Decimal("80000.00")
    )

    result = process_transaction(
        account_id=1,
        transaction=transaction,
        transaction_type="INCOME",
        category="Salary",
        database_path=test_database
    )

    assert result["status"] == "CREATED"

    transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(transactions) == 1
    assert transactions[0]["credit"] == 70000


def test_duplicate_is_skipped(test_database):
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Grocery Store",
        debit=Decimal("500.00")
    )

    first = process_transaction(
        account_id=1,
        transaction=transaction,
        transaction_type="EXPENSE",
        category="Groceries",
        database_path=test_database
    )

    second = process_transaction(
        account_id=1,
        transaction=transaction,
        transaction_type="EXPENSE",
        category="Groceries",
        database_path=test_database
    )

    assert first["status"] == "CREATED"
    assert second["status"] == "DUPLICATE"

    transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(transactions) == 1


def test_balance_is_stored(test_database):
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Grocery Store",
        debit=Decimal("500.00"),
        balance=Decimal("9500.00")
    )

    process_transaction(
        account_id=1,
        transaction=transaction,
        transaction_type="EXPENSE",
        category="Groceries",
        database_path=test_database
    )

    transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert transactions[0]["account_balance"] == 9500


def test_processor_uses_merchant_rule(test_database):
    from src.etrax.database.merchant_rules import create_rule

    create_rule(
        merchant_pattern="SWIGGY",
        category="Dining",
        subcategory="Food Delivery",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="SWIGGY INDIA",
        debit=Decimal("450.00")
    )

    result = process_transaction(
        account_id=1,
        transaction=transaction,
        database_path=test_database
    )

    assert result["status"] == "CREATED"

    transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(transactions) == 1
    assert transactions[0]["transaction_type"] == "EXPENSE"
    assert transactions[0]["category"] == "Dining"
    assert transactions[0]["subcategory"] == "Food Delivery"
    assert transactions[0]["confidence"] == 1.0
    assert transactions[0]["needs_review"] == 0


def test_unknown_transaction_needs_review(test_database):
    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 2),
        description="UNKNOWN PAYMENT XYZ",
        debit=Decimal("250.00")
    )

    result = process_transaction(
        account_id=1,
        transaction=transaction,
        database_path=test_database
    )

    assert result["status"] == "CREATED"

    transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(transactions) == 1
    assert transactions[0]["transaction_type"] == "OTHER"
    assert transactions[0]["category"] == "Other"
    assert transactions[0]["confidence"] == 0.0
    assert transactions[0]["needs_review"] == 1