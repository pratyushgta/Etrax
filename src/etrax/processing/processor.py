from .models import NormalizedTransaction
from .classifier import classify_transaction

from ..database.transactions import (
    create_transaction,
    generate_transaction_hash,
    transaction_exists
)


def process_transaction(
    account_id,
    transaction,
    transaction_type=None,
    category=None,
    subcategory=None,
    statement_id=None,
    database_path=None
):
    if not isinstance(transaction, NormalizedTransaction):
        raise TypeError(
            "transaction must be a NormalizedTransaction"
        )

    # Use deterministic classification when the caller
    # has not explicitly supplied a transaction type/category.
    if transaction_type is None or category is None:
        classification = classify_transaction(
            transaction.description,
            database_path=database_path
        )

        if transaction_type is None:
            transaction_type = classification["transaction_type"]

        if category is None:
            category = classification["category"]

        if subcategory is None:
            subcategory = classification["subcategory"]

        confidence = classification["confidence"]
        needs_review = classification["needs_review"]

    else:
        # Explicitly classified transactions don't require
        # merchant-rule classification.
        confidence = 1.0
        needs_review = 0

    transaction_hash = generate_transaction_hash(
        account_id=account_id,
        transaction_date=transaction.transaction_date.isoformat(),
        description=transaction.description,
        debit=float(transaction.debit),
        credit=float(transaction.credit),
        transaction_time=transaction.transaction_time
    )

    if transaction_exists(
        transaction_hash,
        database_path=database_path
    ):
        return create_transaction(
            account_id=account_id,
            transaction_date=transaction.transaction_date.isoformat(),
            description=transaction.description,
            transaction_type=transaction_type,
            category=category,
            subcategory=subcategory,
            debit=float(transaction.debit),
            credit=float(transaction.credit),
            account_balance=(
                float(transaction.balance)
                if transaction.balance is not None
                else None
            ),
            statement_id=statement_id,
            confidence=confidence,
            needs_review=needs_review,
            transaction_hash=transaction_hash,
            transaction_time=transaction.transaction_time,
            database_path=database_path
        )

    return create_transaction(
        account_id=account_id,
        transaction_date=transaction.transaction_date.isoformat(),
        description=transaction.description,
        transaction_type=transaction_type,
        category=category,
        subcategory=subcategory,
        debit=float(transaction.debit),
        credit=float(transaction.credit),
        account_balance=(
            float(transaction.balance)
            if transaction.balance is not None
            else None
        ),
        statement_id=statement_id,
        confidence=confidence,
        needs_review=needs_review,
        transaction_hash=transaction_hash,
        transaction_time=transaction.transaction_time,
        database_path=database_path
    )