import hashlib
import sqlite3
from .connection import get_connection

def generate_transaction_hash(
    account_id,
    transaction_date,
    description,
    debit=0,
    credit=0,
    transaction_time=None
):
    raw_data = "|".join([
        str(account_id),
        str(transaction_date),
        str(transaction_time or ""),
        str(description).strip().upper(),
        f"{debit:.2f}",
        f"{credit:.2f}"
    ])

    return hashlib.sha256(
        raw_data.encode("utf-8")
    ).hexdigest()

def transaction_exists(transaction_hash, database_path=None):
    with get_connection(database_path) as conn:
        result = conn.execute("""
            SELECT transaction_id
            FROM transactions
            WHERE transaction_hash = ?
            LIMIT 1
        """, (transaction_hash,)).fetchone()

        return result is not None

    
def create_transaction(
    account_id,
    transaction_date,
    description,
    transaction_type,
    category=None,
    subcategory=None,
    debit=0,
    credit=0,
    account_balance=None,
    transfer_id=None,
    investment_id=None,
    goal_id=None,
    statement_id=None,
    confidence=None,
    needs_review=0,
    transaction_hash=None,
    transaction_time=None,
    database_path=None
):
    with get_connection(database_path) as conn:
        try:
            cursor = conn.execute("""
                INSERT INTO transactions (
                    account_id,
                    transaction_date,
                    transaction_time,
                    description,
                    transaction_type,
                    category,
                    subcategory,
                    debit,
                    credit,
                    account_balance,
                    transfer_id,
                    investment_id,
                    goal_id,
                    statement_id,
                    confidence,
                    needs_review,
                    transaction_hash
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                account_id,
                transaction_date,
                transaction_time,
                description,
                transaction_type,
                category,
                subcategory,
                debit,
                credit,
                account_balance,
                transfer_id,
                investment_id,
                goal_id,
                statement_id,
                confidence,
                needs_review,
                transaction_hash
            ))

            return {
                "status": "CREATED",
                "transaction_id": cursor.lastrowid
            }

        except sqlite3.IntegrityError as error:
            if transaction_hash is not None:
                existing = conn.execute("""
                    SELECT transaction_id
                    FROM transactions
                    WHERE transaction_hash = ?
                    LIMIT 1
                """, (transaction_hash,)).fetchone()

                if existing is not None:
                    return {
                        "status": "DUPLICATE",
                        "transaction_id": existing["transaction_id"]
                    }

            raise error
    
def get_transaction(transaction_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                transaction_id,
                account_id,
                transaction_date,
                transaction_time,
                description,
                transaction_type,
                category,
                subcategory,
                debit,
                credit,
                account_balance,
                transfer_id,
                investment_id,
                goal_id,
                confidence,
                needs_review,
                statement_id
            FROM transactions
            WHERE transaction_id = ?
        """, (transaction_id,)).fetchone()


def list_transactions(
    account_id=None,
    start_date=None,
    end_date=None,
    database_path=None
):
    query = """
        SELECT
            transaction_id,
            account_id,
            transaction_date,
            transaction_time,
            description,
            transaction_type,
            category,
            subcategory,
            debit,
            credit,
            account_balance,
            transfer_id,
            investment_id,
            goal_id,
            confidence,
            needs_review,
            statement_id
        FROM transactions
        WHERE 1 = 1
    """

    params = []

    if account_id is not None:
        query += " AND account_id = ?"
        params.append(account_id)

    if start_date is not None:
        query += " AND transaction_date >= ?"
        params.append(start_date)

    if end_date is not None:
        query += " AND transaction_date < ?"
        params.append(end_date)

    query += """
        ORDER BY
            transaction_date,
            transaction_id
    """

    with get_connection(database_path) as conn:
        return conn.execute(query, params).fetchall()


def total_spending(start_date=None, end_date=None):
    query = """
        SELECT COALESCE(SUM(debit), 0)
        FROM transactions
        WHERE transaction_type IN (
            'EXPENSE',
            'BANK_CHARGE'
        )
    """

    params = []

    if start_date is not None:
        query += " AND transaction_date >= ?"
        params.append(start_date)

    if end_date is not None:
        query += " AND transaction_date < ?"
        params.append(end_date)

    with get_connection() as conn:
        return conn.execute(query, params).fetchone()[0]