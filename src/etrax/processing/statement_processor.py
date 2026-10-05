from .reconciliation import reconcile_statement

from ..database.statements import (
    update_statement_status,
    update_statement_results
)

from ..database.balance_snapshots import (
    create_snapshot
)

from .processor import process_transaction


def process_statement(
    statement_id,
    account_id,
    month,
    opening_balance,
    transactions,
    statement_closing_balance,
    database_path=None
):
    """
    Process a normalized bank statement.

    Returns a processing summary.
    """

    update_statement_status(
        statement_id,
        "PROCESSING",
        database_path=database_path
    )

    try:
        reconciliation = reconcile_statement(
            opening_balance=opening_balance,
            transactions=transactions,
            statement_closing_balance=statement_closing_balance
        )

        # Store statement-level information.
        update_statement_results(
            statement_id=statement_id,
            transaction_count=reconciliation["transaction_count"],
            opening_balance=reconciliation["opening_balance"],
            closing_balance=reconciliation[
                "statement_closing_balance"
            ],
            database_path=database_path
        )

        # Store the balance snapshot regardless of validation
        # result. This gives us an audit trail.
        snapshot_id = create_snapshot(
            account_id=account_id,
            month=month,
            opening_balance=(
                float(reconciliation["opening_balance"])
                if reconciliation["opening_balance"] is not None
                else None
            ),
            total_credits=float(
                reconciliation["total_credits"]
            ),
            total_debits=float(
                reconciliation["total_debits"]
            ),
            calculated_closing_balance=(
                float(
                    reconciliation["calculated_closing_balance"]
                )
                if reconciliation["calculated_closing_balance"]
                is not None
                else None
            ),
            statement_closing_balance=(
                float(
                    reconciliation["statement_closing_balance"]
                )
                if reconciliation["statement_closing_balance"]
                is not None
                else None
            ),
            difference=(
                float(reconciliation["difference"])
                if reconciliation["difference"] is not None
                else None
            ),
            validation_status=reconciliation[
                "validation_status"
            ],
            transaction_count=reconciliation[
                "transaction_count"
            ],
            database_path=database_path
        )

        # Never import transactions from an invalid statement.
        if reconciliation["validation_status"] != "VALID":
            update_statement_status(
                statement_id,
                "FAILED",
                database_path=database_path
            )

            return {
                "status": "FAILED",
                "reason": reconciliation[
                    "validation_status"
                ],
                "snapshot_id": snapshot_id,
                "transaction_count": 0
            }

        processed_transactions = []

        for transaction in transactions:
            result = process_transaction(
                account_id=account_id,
                transaction=transaction,
                statement_id=statement_id,
                database_path=database_path
            )

            processed_transactions.append(result)

        update_statement_status(
            statement_id,
            "PROCESSED",
            database_path=database_path
        )

        created_count = sum(
            1
            for result in processed_transactions
            if result["status"] == "CREATED"
        )

        duplicate_count = sum(
            1
            for result in processed_transactions
            if result["status"] == "DUPLICATE"
        )

        return {
            "status": "PROCESSED",
            "snapshot_id": snapshot_id,
            "transaction_count": len(transactions),
            "created_count": created_count,
            "duplicate_count": duplicate_count
        }

    except Exception:
        update_statement_status(
            statement_id,
            "FAILED",
            database_path=database_path
        )

        raise