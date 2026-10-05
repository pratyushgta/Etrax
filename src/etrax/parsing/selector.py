from pathlib import Path

from .csv_parser import CSVStatementParser
from .xlsx_parser import XLSXStatementParser


PARSERS = {
    ".csv": CSVStatementParser,
    ".xlsx": XLSXStatementParser,
}


def get_parser(file_path: Path):
    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    parser_class = PARSERS.get(extension)

    if parser_class is None:
        raise ValueError(
            f"Unsupported statement file type: {extension}"
        )

    return parser_class()