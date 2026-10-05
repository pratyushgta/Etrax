import sqlite3
import pytest


@pytest.fixture
def test_database(tmp_path):
    database_path = tmp_path / "test.db"

    conn = sqlite3.connect(database_path)

    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("""
        CREATE TABLE accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT NOT NULL,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            account_number_masked TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_time TEXT,
            description TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            category TEXT,
            subcategory TEXT,
            debit REAL NOT NULL DEFAULT 0,
            credit REAL NOT NULL DEFAULT 0,
            account_balance REAL,
            transfer_id INTEGER,
            investment_id INTEGER,
            goal_id INTEGER,
            statement_id INTEGER,
            confidence REAL,
            needs_review INTEGER NOT NULL DEFAULT 0,
            transaction_hash TEXT,
            UNIQUE (transaction_hash),

            FOREIGN KEY (account_id)
                REFERENCES accounts(account_id),
    
            CHECK (debit >= 0),
            CHECK (credit >= 0),

            CHECK (
                NOT (debit > 0 AND credit > 0)
            ),

            CHECK (
                transaction_type IN (
                    'INCOME',
                    'EXPENSE',
                    'TRANSFER',
                    'INVESTMENT',
                    'INVESTMENT_REDEMPTION',
                    'INTEREST',
                    'REFUND',
                    'BANK_CHARGE',
                    'OTHER'
                )
            )
        )
    """)

    conn.execute("""
        CREATE TABLE statements (
            statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            statement_period_start TEXT,
            statement_period_end TEXT,
            opening_balance REAL,
            closing_balance REAL,
            transaction_count INTEGER DEFAULT 0,
            processing_status TEXT NOT NULL DEFAULT 'PENDING',
            uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (account_id)
                REFERENCES accounts(account_id)
        )
    """)


    conn.execute("""
        CREATE TABLE merchant_rules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_pattern TEXT NOT NULL,
            category TEXT,
            subcategory TEXT,
            transaction_type TEXT,
            priority INTEGER NOT NULL DEFAULT 100,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)


    conn.execute("""
        CREATE TABLE balance_snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            opening_balance REAL,
            total_credits REAL DEFAULT 0,
            total_debits REAL DEFAULT 0,
            calculated_closing_balance REAL,
            statement_closing_balance REAL,
            difference REAL,
            validation_status TEXT,
            transaction_count INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (account_id)
                REFERENCES accounts(account_id),

            CHECK (
                validation_status IN (
                    'PENDING',
                    'VALID',
                    'MISMATCH',
                    'INCOMPLETE'
                )
            ),

            UNIQUE (account_id, month)
        )
    """)

    
    
    conn.execute("""
        INSERT INTO accounts (
            bank_name,
            account_name,
            account_type
        )
        VALUES (
            'Test Bank',
            'Test Account',
            'SAVINGS'
        )
    """)

    conn.commit()
    conn.close()

    return database_path