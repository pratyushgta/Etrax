from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NormalizedTransaction:
    transaction_date: date
    description: str
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    transaction_time: Optional[str] = None
    balance: Optional[Decimal] = None

    def __post_init__(self):
        if self.debit < 0:
            raise ValueError("Debit cannot be negative")

        if self.credit < 0:
            raise ValueError("Credit cannot be negative")

        if self.debit > 0 and self.credit > 0:
            raise ValueError(
                "A transaction cannot have both debit and credit"
            )

        if not self.description.strip():
            raise ValueError(
                "Transaction description cannot be empty"
            )