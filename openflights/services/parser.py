"""
CSV parser service for OpenFlights data files.

Parses DAT/CSV files from OpenFlights and yields records.
"""

import csv
import logging
from pathlib import Path
from typing import Generator, List

from ..conf import (
    AIRLINE_FIELDS,
    AIRPORT_FIELDS,
    LOGGER_NAME,
    PLANE_FIELDS,
)
from ..exceptions import ParseError
from ..util import parse_openflights_null

logger = logging.getLogger(LOGGER_NAME)


class CSVParser:
    """
    Parser for OpenFlights CSV/DAT data files.

    OpenFlights uses CSV format with:
    - Comma delimiter
    - Double-quote text qualifier
    - \\N for NULL values
    """

    # Field definitions for each data type
    FIELD_DEFS = {
        "airports": AIRPORT_FIELDS,
        "airlines": AIRLINE_FIELDS,
        "planes": PLANE_FIELDS,
    }

    def __init__(self, file_path: Path, data_type: str, quiet: bool = False):
        """
        Initialize the parser.

        Args:
            file_path: Path to data file
            data_type: Type of data (airports, airlines, planes)
            quiet: If True, suppress progress output
        """
        self.file_path = Path(file_path)
        self.data_type = data_type
        self.quiet = quiet

        if not self.file_path.exists():
            raise ParseError(f"File not found: {file_path}")

        self.fields = self.FIELD_DEFS.get(data_type)
        if not self.fields:
            raise ParseError(f"Unknown data type: {data_type}")

    def count_records(self) -> int:
        """
        Count total records in the file.

        Returns:
            Number of records
        """
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)

    def iter_records(self) -> Generator[dict, None, None]:
        """
        Iterate over records in the file.

        Yields:
            Dict with field names as keys
        """
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)

            for row_num, row in enumerate(reader, 1):
                try:
                    record = self._parse_row(row, row_num)
                    if record:
                        yield record
                except Exception as e:
                    logger.warning("Error parsing row %d: %s", row_num, e)

    def _parse_row(self, row: List[str], row_num: int) -> dict:
        """
        Parse a single CSV row into a dict.

        Args:
            row: List of field values
            row_num: Row number for error messages

        Returns:
            Dict with field names and cleaned values
        """
        # Handle rows with different field counts
        if len(row) < len(self.fields):
            # Pad with empty strings
            row = row + [""] * (len(self.fields) - len(row))
        elif len(row) > len(self.fields):
            # Truncate
            row = row[: len(self.fields)]

        # Build dict with cleaned values
        record = {}
        for i, field_name in enumerate(self.fields):
            value = row[i] if i < len(row) else ""
            record[field_name] = parse_openflights_null(value)

        return record

    def get_records(self, limit: int = None) -> list:
        """
        Get all records as a list.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of record dicts
        """
        records = []
        for record in self.iter_records():
            records.append(record)
            if limit and len(records) >= limit:
                break
        return records


def parse_airports_file(file_path: Path, quiet: bool = False) -> Generator[dict, None, None]:
    """
    Parse airports data file.

    Args:
        file_path: Path to airports-extended.dat
        quiet: If True, suppress output

    Yields:
        Airport record dicts
    """
    parser = CSVParser(file_path, "airports", quiet=quiet)
    yield from parser.iter_records()


def parse_airlines_file(file_path: Path, quiet: bool = False) -> Generator[dict, None, None]:
    """
    Parse airlines data file.

    Args:
        file_path: Path to airlines.dat
        quiet: If True, suppress output

    Yields:
        Airline record dicts
    """
    parser = CSVParser(file_path, "airlines", quiet=quiet)
    yield from parser.iter_records()


def parse_planes_file(file_path: Path, quiet: bool = False) -> Generator[dict, None, None]:
    """
    Parse planes/aircraft data file.

    Args:
        file_path: Path to planes.dat
        quiet: If True, suppress output

    Yields:
        Plane record dicts
    """
    parser = CSVParser(file_path, "planes", quiet=quiet)
    yield from parser.iter_records()
