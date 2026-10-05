import sqlite3

from src.etrax.database.statements import (
    create_statement,
    get_statement,
    list_statements,
    update_statement_status,
    update_statement_results
)


def test_create_statement(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="abc123",
        database_path=test_database
    )

    assert statement_id == 1


def test_statement_defaults_to_pending(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="abc123",
        database_path=test_database
    )

    statement = get_statement(
        statement_id,
        database_path=test_database
    )

    assert statement["processing_status"] == "PENDING"
    assert statement["transaction_count"] == 0


def test_list_statements(test_database):
    create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="abc123",
        database_path=test_database
    )

    statements = list_statements(
        account_id=1,
        database_path=test_database
    )

    assert len(statements) == 1
    assert statements[0]["file_name"] == "October_2026.pdf"


def test_update_statement_status(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="abc123",
        database_path=test_database
    )

    update_statement_status(
        statement_id,
        "PROCESSING",
        database_path=test_database
    )

    statement = get_statement(
        statement_id,
        database_path=test_database
    )

    assert statement["processing_status"] == "PROCESSING"


def test_update_statement_results(test_database):
    statement_id = create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="abc123",
        database_path=test_database
    )

    update_statement_results(
        statement_id=statement_id,
        transaction_count=25,
        opening_balance=10000,
        closing_balance=15000,
        statement_period_start="2026-10-01",
        statement_period_end="2026-10-31",
        database_path=test_database
    )

    statement = get_statement(
        statement_id,
        database_path=test_database
    )

    assert statement["transaction_count"] == 25
    assert statement["opening_balance"] == 10000
    assert statement["closing_balance"] == 15000
    assert statement["statement_period_start"] == "2026-10-01"
    assert statement["statement_period_end"] == "2026-10-31"


def test_duplicate_statement_is_rejected(test_database):
    create_statement(
        account_id=1,
        file_name="October_2026.pdf",
        file_hash="abc123",
        database_path=test_database
    )

    try:
        create_statement(
            account_id=1,
            file_name="October_2026_copy.pdf",
            file_hash="abc123",
            database_path=test_database
        )
    except sqlite3.IntegrityError:
        return

    raise AssertionError(
        "Duplicate statement file hash should be rejected"
    )