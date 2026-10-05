from decimal import Decimal
from pathlib import Path

import pytest

from etrax.parsing.csv_parser import CSVStatementParser


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "sample_statement.csv"
)


def test_csv_parser_returns_normalized_statement():
    parser = CSVStatementParser()

    result = parser.parse(
        file_path=FIXTURE,
        account_id=1,
    )

    assert result.account_id == 1

    assert result.statement_period_start.isoformat() == "2026-09-01"
    assert result.statement_period_end.isoformat() == "2026-09-04"

    assert result.closing_balance == Decimal("58000")

    assert len(result.transactions) == 4


def test_csv_parser_normalizes_transaction():
    parser = CSVStatementParser()

    result = parser.parse(
        file_path=FIXTURE,
        account_id=1,
    )

    transaction = result.transactions[1]

    assert transaction.transaction_date.isoformat() == "2026-09-02"
    assert transaction.description == "FreshMart Grocery"

    assert transaction.debit == Decimal("4000")
    assert transaction.credit == Decimal("0")

    assert transaction.balance == Decimal("76000")


def test_csv_parser_rejects_missing_required_column(tmp_path):
    csv_file = tmp_path / "invalid.csv"

    csv_file.write_text(
        "Date,Description,Credit\n"
        "2026-09-01,Salary,70000\n",
        encoding="utf-8",
    )

    parser = CSVStatementParser()

    with pytest.raises(ValueError, match="Missing required CSV columns"):
        parser.parse(csv_file, account_id=1)


def test_csv_parser_rejects_invalid_amount(tmp_path):
    csv_file = tmp_path / "invalid.csv"

    csv_file.write_text(
        "Date,Description,Debit,Credit\n"
        "2026-09-01,Salary,ABC,0\n",
        encoding="utf-8",
    )

    parser = CSVStatementParser()

    with pytest.raises(ValueError, match="Invalid Debit amount"):
        parser.parse(csv_file, account_id=1)


def test_csv_parser_rejects_empty_description(tmp_path):
    csv_file = tmp_path / "invalid.csv"

    csv_file.write_text(
        "Date,Description,Debit,Credit\n"
        "2026-09-01,,100,0\n",
        encoding="utf-8",
    )

    parser = CSVStatementParser()

    with pytest.raises(
        ValueError,
        match="Description cannot be empty"
    ):
        parser.parse(csv_file, account_id=1)