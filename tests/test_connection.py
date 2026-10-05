import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.etrax.database.connection import (
    get_connection,
    get_database_path
)


def test_database_exists():
    assert get_database_path().exists()


def test_database_connection():
    with get_connection() as conn:
        result = conn.execute(
            "SELECT 1"
        ).fetchone()

        assert result[0] == 1


def test_foreign_keys_enabled():
    with get_connection() as conn:
        result = conn.execute(
            "PRAGMA foreign_keys"
        ).fetchone()

        assert result[0] == 1