from .connection import get_connection


def create_rule(
    merchant_pattern,
    category=None,
    subcategory=None,
    transaction_type=None,
    priority=100,
    database_path=None
):
    with get_connection(database_path) as conn:
        cursor = conn.execute("""
            INSERT INTO merchant_rules (
                merchant_pattern,
                category,
                subcategory,
                transaction_type,
                priority
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            merchant_pattern,
            category,
            subcategory,
            transaction_type,
            priority
        ))

        return cursor.lastrowid


def get_rule(rule_id, database_path=None):
    with get_connection(database_path) as conn:
        return conn.execute("""
            SELECT
                rule_id,
                merchant_pattern,
                category,
                subcategory,
                transaction_type,
                priority,
                is_active
            FROM merchant_rules
            WHERE rule_id = ?
        """, (rule_id,)).fetchone()


def list_rules(database_path=None):
    with get_connection(database_path) as conn:
        return conn.execute("""
            SELECT
                rule_id,
                merchant_pattern,
                category,
                subcategory,
                transaction_type,
                priority,
                is_active
            FROM merchant_rules
            WHERE is_active = 1
            ORDER BY priority DESC, rule_id
        """).fetchall()


def find_matching_rule(description, database_path=None):
    with get_connection(database_path) as conn:
        return conn.execute("""
            SELECT
                rule_id,
                merchant_pattern,
                category,
                subcategory,
                transaction_type,
                priority,
                is_active
            FROM merchant_rules
            WHERE is_active = 1
              AND LOWER(?) LIKE '%' || LOWER(merchant_pattern) || '%'
            ORDER BY priority DESC, rule_id
            LIMIT 1
        """, (description,)).fetchone()