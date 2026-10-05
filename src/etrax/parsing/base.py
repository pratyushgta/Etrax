from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional, Protocol

from ..processing.models import NormalizedTransaction


@dataclass(frozen=True)
class NormalizedStatement:
    account_id: int
    statement_period_start: Optional[date]
    statement_period_end: Optional[date]
    opening_balance: Optional[Decimal]
    closing_balance: Optional[Decimal]
    transactions: list[NormalizedTransaction]


class StatementParser(Protocol):
    def parse(
        self,
        file_path: Path,
        account_id: int
    ) -> NormalizedStatement:
        ...