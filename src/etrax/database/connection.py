from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "database" / "etrax.db"


def get_connection(database_path=None) -> sqlite3.Connection:
    if database_path is None:
        database_path = DATABASE_PATH

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def get_database_path() -> Path:
    return DATABASE_PATH