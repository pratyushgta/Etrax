from .connection import get_connection


def create_snapshot(
    account_id,
    month,
    opening_balance=None,
    total_credits=0,
    total_debits=0,
    calculated_closing_balance=None,
    statement_closing_balance=None,
    difference=None,
    validation_status="PENDING",
    transaction_count=0,
    database_path=None
):
    with get_connection(database_path) as conn:
        cursor = conn.execute("""
            INSERT INTO balance_snapshots (
                account_id,
                month,
                opening_balance,
                total_credits,
                total_debits,
                calculated_closing_balance,
                statement_closing_balance,
                difference,
                validation_status,
                transaction_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_id,
            month,
            opening_balance,
            total_credits,
            total_debits,
            calculated_closing_balance,
            statement_closing_balance,
            difference,
            validation_status,
            transaction_count
        ))

        return cursor.lastrowid


def get_snapshot(
    account_id,
    month,
    database_path=None
):
    with get_connection(database_path) as conn:
        return conn.execute("""
            SELECT
                snapshot_id,
                account_id,
                month,
                opening_balance,
                total_credits,
                total_debits,
                calculated_closing_balance,
                statement_closing_balance,
                difference,
                validation_status,
                transaction_count
            FROM balance_snapshots
            WHERE account_id = ?
              AND month = ?
        """, (
            account_id,
            month
        )).fetchone()


def update_snapshot_validation(
    snapshot_id,
    calculated_closing_balance,
    statement_closing_balance,
    difference,
    validation_status,
    database_path=None
):
    with get_connection(database_path) as conn:
        conn.execute("""
            UPDATE balance_snapshots
            SET
                calculated_closing_balance = ?,
                statement_closing_balance = ?,
                difference = ?,
                validation_status = ?
            WHERE snapshot_id = ?
        """, (
            calculated_closing_balance,
            statement_closing_balance,
            difference,
            validation_status,
            snapshot_id
        ))