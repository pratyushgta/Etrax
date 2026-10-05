from decimal import Decimal


VALIDATION_VALID = "VALID"
VALIDATION_MISMATCH = "MISMATCH"
VALIDATION_INCOMPLETE = "INCOMPLETE"


def calculate_closing_balance(
    opening_balance,
    total_credits,
    total_debits
):
    opening = Decimal(str(opening_balance))
    credits = Decimal(str(total_credits))
    debits = Decimal(str(total_debits))

    return opening + credits - debits


def validate_balance(
    opening_balance,
    total_credits,
    total_debits,
    statement_closing_balance,
    tolerance=Decimal("0.01")
):
    if (
        opening_balance is None
        or total_credits is None
        or total_debits is None
        or statement_closing_balance is None
    ):
        return {
            "validation_status": VALIDATION_INCOMPLETE,
            "calculated_closing": None,
            "difference": None
        }

    calculated_closing = calculate_closing_balance(
        opening_balance,
        total_credits,
        total_debits
    )

    statement_closing = Decimal(
        str(statement_closing_balance)
    )

    difference = calculated_closing - statement_closing

    if abs(difference) <= tolerance:
        status = VALIDATION_VALID
    else:
        status = VALIDATION_MISMATCH

    return {
        "validation_status": status,
        "calculated_closing": calculated_closing,
        "difference": difference
    }