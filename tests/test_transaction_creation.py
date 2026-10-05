from src.etrax.database.transactions import (
    create_transaction,
    generate_transaction_hash,
    transaction_exists
)

import sqlite3

from src.etrax.database.transactions import create_transaction


def test_create_expense(test_database):
    transaction_id = create_transaction(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Grocery Store",
        transaction_type="EXPENSE",
        category="Groceries",
        debit=500,
        database_path=test_database
    )

    assert transaction_id["status"] == "CREATED"
    assert transaction_id["transaction_id"] == 1
    #assert transaction_id == 1


def test_create_income(test_database):
    transaction_id = create_transaction(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Salary",
        transaction_type="INCOME",
        credit=70000,
        database_path=test_database
    )

    assert transaction_id["status"] == "CREATED"
    assert transaction_id["transaction_id"] == 1
    #assert transaction_id == 1


def test_debit_and_credit_cannot_both_be_positive(test_database):
    try:
        create_transaction(
            account_id=1,
            transaction_date="2026-10-01",
            description="Invalid Transaction",
            transaction_type="OTHER",
            debit=100,
            credit=100,
            database_path=test_database
        )
    except sqlite3.IntegrityError:
        return

    raise AssertionError(
        "Transaction with both debit and credit should fail"
    )


def test_invalid_account_is_rejected(test_database):
    try:
        create_transaction(
            account_id=999,
            transaction_date="2026-10-01",
            description="Invalid Account",
            transaction_type="EXPENSE",
            debit=100,
            database_path=test_database
        )
    except sqlite3.IntegrityError:
        return

    raise AssertionError(
        "Transaction with invalid account should fail"
    )

def test_transaction_hash_is_deterministic():
    hash_1 = generate_transaction_hash(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Grocery Store",
        debit=500
    )

    hash_2 = generate_transaction_hash(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Grocery Store",
        debit=500
    )

    assert hash_1 == hash_2


def test_different_transactions_have_different_hashes():
    hash_1 = generate_transaction_hash(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Grocery Store",
        debit=500
    )

    hash_2 = generate_transaction_hash(
        account_id=1,
        transaction_date="2026-10-02",
        description="Test Grocery Store",
        debit=500
    )

    assert hash_1 != hash_2


def test_transaction_exists(test_database):
    transaction_hash = generate_transaction_hash(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Grocery Store",
        debit=500
    )

    create_transaction(
        account_id=1,
        transaction_date="2026-10-01",
        description="Test Grocery Store",
        transaction_type="EXPENSE",
        category="Groceries",
        debit=500,
        transaction_hash=transaction_hash,
        database_path=test_database
    )

    assert transaction_exists(
        transaction_hash,
        database_path=test_database
    )


def test_duplicate_transaction_is_rejected(test_database):
    transaction_hash = generate_transaction_hash(
        account_id=1,
        transaction_date="2026-10-01",
        description="Duplicate Grocery",
        debit=500
    )

    first = create_transaction(
        account_id=1,
        transaction_date="2026-10-01",
        description="Duplicate Grocery",
        transaction_type="EXPENSE",
        category="Groceries",
        debit=500,
        transaction_hash=transaction_hash,
        database_path=test_database
    )

    second = create_transaction(
        account_id=1,
        transaction_date="2026-10-01",
        description="Duplicate Grocery",
        transaction_type="EXPENSE",
        category="Groceries",
        debit=500,
        transaction_hash=transaction_hash,
        database_path=test_database
    )

    assert first["status"] == "CREATED"
    assert second["status"] == "DUPLICATE"
    assert second["transaction_id"] == first["transaction_id"]