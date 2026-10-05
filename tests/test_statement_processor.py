from datetime import date
from decimal import Decimal

from src.etrax.processing.models import NormalizedTransaction
from src.etrax.processing.statement_processor import (
    process_statement
)

from src.etrax.database.statements import (
    create_statement,
    get_statement
)

from src.etrax.database.balance_snapshots import (
    get_snapshot
)

from src.etrax.database.transactions import (
    list_transactions
)


def test_valid_statement_is_processed(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="statement-hash-1",
        database_path=test_database
    )

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

    result = process_statement(
        statement_id=statement_id,
        account_id=1,
        month="2026-10",
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=73000,
        database_path=test_database
    )

    assert result["status"] == "PROCESSED"
    assert result["transaction_count"] == 3
    assert result["created_count"] == 3
    assert result["duplicate_count"] == 0

    statement = get_statement(
        statement_id,
        database_path=test_database
    )

    assert statement["processing_status"] == "PROCESSED"

    snapshot = get_snapshot(
        account_id=1,
        month="2026-10",
        database_path=test_database
    )

    assert snapshot["validation_status"] == "VALID"
    assert snapshot["calculated_closing_balance"] == 73000


def test_mismatched_statement_is_not_imported(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="Bad_Statement.pdf",
        file_hash="statement-hash-2",
        database_path=test_database
    )

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

    result = process_statement(
        statement_id=statement_id,
        account_id=1,
        month="2026-11",
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=70000,
        database_path=test_database
    )

    assert result["status"] == "FAILED"
    assert result["reason"] == "MISMATCH"
    assert result["transaction_count"] == 0

    statement = get_statement(
        statement_id,
        database_path=test_database
    )

    assert statement["processing_status"] == "FAILED"

    stored_transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(stored_transactions) == 0


def test_incomplete_statement_is_not_imported(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="Incomplete.pdf",
        file_hash="statement-hash-3",
        database_path=test_database
    )

    transactions = [
        NormalizedTransaction(
            transaction_date=date(2026, 10, 1),
            description="Salary",
            credit=Decimal("70000")
        )
    ]

    result = process_statement(
        statement_id=statement_id,
        account_id=1,
        month="2026-12",
        opening_balance=10000,
        transactions=transactions,
        statement_closing_balance=None,
        database_path=test_database
    )

    assert result["status"] == "FAILED"
    assert result["reason"] == "INCOMPLETE"

    stored_transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(stored_transactions) == 0


def test_duplicate_transactions_are_skipped(
    test_database
):
    statement_id = create_statement(
        account_id=1,
        file_name="Duplicate_Test.pdf",
        file_hash="statement-hash-4",
        database_path=test_database
    )

    transaction = NormalizedTransaction(
        transaction_date=date(2026, 10, 1),
        description="Salary",
        credit=Decimal("70000")
    )

    first_result = process_statement(
        statement_id=statement_id,
        account_id=1,
        month="2027-01",
        opening_balance=10000,
        transactions=[transaction],
        statement_closing_balance=80000,
        database_path=test_database
    )

    assert first_result["created_count"] == 1

    second_result = process_statement(
        statement_id=statement_id,
        account_id=1,
        month="2027-02",
        opening_balance=10000,
        transactions=[transaction],
        statement_closing_balance=80000,
        database_path=test_database
    )

    assert second_result["duplicate_count"] == 1

    stored_transactions = list_transactions(
        account_id=1,
        database_path=test_database
    )

    assert len(stored_transactions) == 1