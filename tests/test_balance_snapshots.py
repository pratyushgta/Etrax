import sqlite3

from src.etrax.database.balance_snapshots import (
    create_snapshot,
    get_snapshot,
    update_snapshot_validation
)


def test_create_snapshot(test_database):
    snapshot_id = create_snapshot(
        account_id=1,
        month="2026-10",
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        validation_status="PENDING",
        transaction_count=4,
        database_path=test_database
    )

    assert snapshot_id == 1


def test_get_snapshot(test_database):
    create_snapshot(
        account_id=1,
        month="2026-10",
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        validation_status="PENDING",
        transaction_count=4,
        database_path=test_database
    )

    snapshot = get_snapshot(
        account_id=1,
        month="2026-10",
        database_path=test_database
    )

    assert snapshot is not None
    assert snapshot["opening_balance"] == 10000
    assert snapshot["total_credits"] == 70000
    assert snapshot["total_debits"] == 22000
    assert snapshot["transaction_count"] == 4


def test_update_snapshot_validation(test_database):
    snapshot_id = create_snapshot(
        account_id=1,
        month="2026-10",
        opening_balance=10000,
        total_credits=70000,
        total_debits=22000,
        validation_status="PENDING",
        database_path=test_database
    )

    update_snapshot_validation(
        snapshot_id=snapshot_id,
        calculated_closing_balance=58000,
        statement_closing_balance=58000,
        difference=0,
        validation_status="VALID",
        database_path=test_database
    )

    snapshot = get_snapshot(
        account_id=1,
        month="2026-10",
        database_path=test_database
    )

    assert snapshot["calculated_closing_balance"] == 58000
    assert snapshot["statement_closing_balance"] == 58000
    assert snapshot["difference"] == 0
    assert snapshot["validation_status"] == "VALID"


def test_duplicate_month_is_rejected(test_database):
    create_snapshot(
        account_id=1,
        month="2026-10",
        database_path=test_database
    )

    try:
        create_snapshot(
            account_id=1,
            month="2026-10",
            database_path=test_database
        )
    except sqlite3.IntegrityError:
        return

    raise AssertionError(
        "Duplicate account/month snapshot should be rejected"
    )