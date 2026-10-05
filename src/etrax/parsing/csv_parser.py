import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .base import NormalizedStatement
from ..processing.models import NormalizedTransaction


class CSVStatementParser:
    """
    Parser for a normalized CSV statement format.

    Required columns:
        Date
        Description
        Debit
        Credit

    Optional columns:
        Balance
        Time
    """

    REQUIRED_COLUMNS = {
        "Date",
        "Description",
        "Debit",
        "Credit",
    }

    def parse(self, file_path: Path, account_id: int) -> NormalizedStatement:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        with file_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file does not contain a header row")

            columns = {
                column.strip()
                for column in reader.fieldnames
                if column is not None
            }

            missing_columns = self.REQUIRED_COLUMNS - columns

            if missing_columns:
                raise ValueError(
                    "Missing required CSV columns: "
                    + ", ".join(sorted(missing_columns))
                )

            transactions = []

            for row_number, row in enumerate(reader, start=2):
                transactions.append(
                    self._parse_transaction(row, row_number)
                )

        if not transactions:
            raise ValueError("CSV statement contains no transactions")

        transactions.sort(key=lambda transaction: transaction.transaction_date)

        statement_period_start = transactions[0].transaction_date
        statement_period_end = transactions[-1].transaction_date

        opening_balance = None
        closing_balance = None

        balances = [
            transaction.balance
            for transaction in transactions
            if transaction.balance is not None
        ]

        if balances:
            closing_balance = balances[-1]

        return NormalizedStatement(
            account_id=account_id,
            statement_period_start=statement_period_start,
            statement_period_end=statement_period_end,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            transactions=transactions,
        )

    @staticmethod
    def _parse_transaction(row, row_number):
        transaction_date = CSVStatementParser._parse_date(
            row["Date"],
            row_number
        )

        description = (row["Description"] or "").strip()

        if not description:
            raise ValueError(
                f"Row {row_number}: Description cannot be empty"
            )

        debit = CSVStatementParser._parse_amount(
            row["Debit"],
            row_number,
            "Debit"
        )

        credit = CSVStatementParser._parse_amount(
            row["Credit"],
            row_number,
            "Credit"
        )

        transaction_time = None

        if "Time" in row and row["Time"]:
            transaction_time = row["Time"].strip()

        balance = None

        if "Balance" in row and row["Balance"]:
            balance = CSVStatementParser._parse_amount(
                row["Balance"],
                row_number,
                "Balance"
            )

        return NormalizedTransaction(
            transaction_date=transaction_date,
            transaction_time=transaction_time,
            description=description,
            debit=debit,
            credit=credit,
            balance=balance,
        )

    @staticmethod
    def _parse_date(value, row_number):
        value = (value or "").strip()

        if not value:
            raise ValueError(
                f"Row {row_number}: Date cannot be empty"
            )

        formats = (
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%Y/%m/%d",
        )

        for date_format in formats:
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue

        raise ValueError(
            f"Row {row_number}: Unsupported date format: {value}"
        )

    @staticmethod
    def _parse_amount(value, row_number, column_name):
        value = (value or "").strip()

        if not value:
            return Decimal("0")

        value = value.replace(",", "")
        value = value.replace("₹", "")
        value = value.strip()

        try:
            amount = Decimal(value)
        except InvalidOperation:
            raise ValueError(
                f"Row {row_number}: Invalid {column_name} amount: {value}"
            )

        if amount < 0:
            raise ValueError(
                f"Row {row_number}: {column_name} cannot be negative"
            )

        return amount