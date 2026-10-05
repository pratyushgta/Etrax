from .connection import get_connection


def create_statement(
    account_id,
    file_name,
    file_hash,
    statement_period_start=None,
    statement_period_end=None,
    opening_balance=None,
    closing_balance=None,
    transaction_count=0,
    database_path=None
):
    with get_connection(database_path) as conn:
        cursor = conn.execute("""
            INSERT INTO statements (
                account_id,
                file_name,
                file_hash,
                statement_period_start,
                statement_period_end,
                opening_balance,
                closing_balance,
                transaction_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_id,
            file_name,
            file_hash,
            statement_period_start,
            statement_period_end,
            opening_balance,
            closing_balance,
            transaction_count
        ))

        return cursor.lastrowid


def get_statement(statement_id, database_path=None):
    with get_connection(database_path) as conn:
        return conn.execute("""
            SELECT
                statement_id,
                account_id,
                file_name,
                file_hash,
                statement_period_start,
                statement_period_end,
                opening_balance,
                closing_balance,
                transaction_count,
                processing_status,
                uploaded_at
            FROM statements
            WHERE statement_id = ?
        """, (statement_id,)).fetchone()


def list_statements(account_id=None, database_path=None):
    query = """
        SELECT
            statement_id,
            account_id,
            file_name,
            file_hash,
            statement_period_start,
            statement_period_end,
            opening_balance,
            closing_balance,
            transaction_count,
            processing_status,
            uploaded_at
        FROM statements
        WHERE 1 = 1
    """

    params = []

    if account_id is not None:
        query += " AND account_id = ?"
        params.append(account_id)

    query += """
        ORDER BY uploaded_at DESC, statement_id DESC
    """

    with get_connection(database_path) as conn:
        return conn.execute(query, params).fetchall()


def update_statement_status(
    statement_id,
    processing_status,
    database_path=None
):
    with get_connection(database_path) as conn:
        conn.execute("""
            UPDATE statements
            SET processing_status = ?
            WHERE statement_id = ?
        """, (
            processing_status,
            statement_id
        ))


def update_statement_results(
    statement_id,
    transaction_count,
    opening_balance=None,
    closing_balance=None,
    statement_period_start=None,
    statement_period_end=None,
    database_path=None
):
    with get_connection(database_path) as conn:
        conn.execute("""
            UPDATE statements
            SET
                transaction_count = ?,
                opening_balance = ?,
                closing_balance = ?,
                statement_period_start = ?,
                statement_period_end = ?
            WHERE statement_id = ?
        """, (
            transaction_count,
            float(opening_balance)
            if opening_balance is not None
            else None,
            float(closing_balance)
            if closing_balance is not None
            else None,
            statement_period_start,
            statement_period_end,
            statement_id
        ))