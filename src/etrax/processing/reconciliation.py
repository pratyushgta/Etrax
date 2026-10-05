from decimal import Decimal

from .balance import validate_balance


def reconcile_statement(
    opening_balance,
    transactions,
    statement_closing_balance
):
    total_credits = Decimal("0")
    total_debits = Decimal("0")

    for transaction in transactions:
        total_credits += transaction.credit
        total_debits += transaction.debit

    result = validate_balance(
        opening_balance=opening_balance,
        total_credits=total_credits,
        total_debits=total_debits,
        statement_closing_balance=statement_closing_balance
    )

    return {
        "opening_balance": Decimal(str(opening_balance))
            if opening_balance is not None
            else None,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "calculated_closing_balance": result[
            "calculated_closing"
        ],
        "statement_closing_balance": (
            Decimal(str(statement_closing_balance))
            if statement_closing_balance is not None
            else None
        ),
        "difference": result["difference"],
        "validation_status": result["validation_status"],
        "transaction_count": len(transactions)
    }