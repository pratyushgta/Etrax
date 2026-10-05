from .connection import get_connection


def list_accounts():
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                account_id,
                bank_name,
                account_name,
                account_type,
                account_number_masked,
                is_active
            FROM accounts
            WHERE is_active = 1
            ORDER BY account_id
        """).fetchall()


def get_account(account_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                account_id,
                bank_name,
                account_name,
                account_type,
                account_number_masked,
                is_active
            FROM accounts
            WHERE account_id = ?
        """, (account_id,)).fetchone()


def create_account(
    bank_name,
    account_name,
    account_type="SAVINGS",
    account_number_masked=None
):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO accounts (
                bank_name,
                account_name,
                account_type,
                account_number_masked
            )
            VALUES (?, ?, ?, ?)
        """, (
            bank_name,
            account_name,
            account_type,
            account_number_masked
        ))

        return cursor.lastrowid