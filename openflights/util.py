"""Utility functions for OpenFlights operations."""

import re
import unicodedata
from typing import Optional

from .conf import FEET_TO_METERS


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert a string to a URL-friendly slug.

    Args:
        value: String to slugify
        allow_unicode: If True, allow unicode characters

    Returns:
        Slugified string
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")

    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def parse_openflights_null(value: str) -> Optional[str]:
    """
    Parse OpenFlights null value.

    OpenFlights uses \\N to represent NULL values.

    Args:
        value: Raw value from CSV

    Returns:
        Cleaned value or None
    """
    if value is None:
        return None
    value = str(value).strip()
    if value in ("\\N", "\\n", "NULL", "null", "", "-"):
        return None
    return value


def parse_int(value, default: Optional[int] = None) -> Optional[int]:
    """
    Parse an integer value.

    Args:
        value: Value to parse
        default: Default if parsing fails

    Returns:
        Parsed integer or default
    """
    cleaned = parse_openflights_null(value)
    if cleaned is None:
        return default
    try:
        return int(cleaned)
    except (ValueError, TypeError):
        return default


def parse_float(value, default: Optional[float] = None) -> Optional[float]:
    """
    Parse a float value.

    Args:
        value: Value to parse
        default: Default if parsing fails

    Returns:
        Parsed float or default
    """
    cleaned = parse_openflights_null(value)
    if cleaned is None:
        return default
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def parse_bool(value, default: bool = False) -> bool:
    """
    Parse a boolean value.

    Args:
        value: Value to parse
        default: Default if parsing fails

    Returns:
        Parsed boolean
    """
    cleaned = parse_openflights_null(value)
    if cleaned is None:
        return default
    return cleaned.upper() in ("Y", "YES", "TRUE", "1", "T")


def feet_to_meters(feet: float) -> float:
    """
    Convert feet to meters.

    Args:
        feet: Altitude in feet

    Returns:
        Altitude in meters
    """
    return feet * FEET_TO_METERS


def clean_iata_code(code: str) -> str:
    """
    Clean and validate IATA code.

    Args:
        code: Raw IATA code

    Returns:
        Cleaned 3-letter code or empty string
    """
    cleaned = parse_openflights_null(code)
    if not cleaned:
        return ""
    cleaned = cleaned.upper().strip()
    if len(cleaned) != 3:
        return ""
    if not cleaned.isalnum():
        return ""
    return cleaned


def clean_icao_code(code: str) -> str:
    """
    Clean and validate ICAO code.

    Args:
        code: Raw ICAO code

    Returns:
        Cleaned 4-letter code or empty string
    """
    cleaned = parse_openflights_null(code)
    if not cleaned:
        return ""
    cleaned = cleaned.upper().strip()
    if len(cleaned) != 4:
        return ""
    if not cleaned.isalnum():
        return ""
    return cleaned


def parse_equipment(equipment: str) -> list:
    """
    Parse equipment/aircraft types.

    Equipment can be space-separated list of aircraft codes.

    Args:
        equipment: Raw equipment string

    Returns:
        List of aircraft codes
    """
    cleaned = parse_openflights_null(equipment)
    if not cleaned:
        return []
    return [code.strip() for code in cleaned.split() if code.strip()]


def normalize_country_name(name: str) -> str:
    """
    Normalize country name for matching.

    Args:
        name: Raw country name

    Returns:
        Normalized name
    """
    if not name:
        return ""

    # Common replacements
    replacements = {
        "United States": "United States of America",
        "USA": "United States of America",
        "UK": "United Kingdom",
        "Russia": "Russian Federation",
        "South Korea": "Korea, Republic of",
        "North Korea": "Korea, Democratic People's Republic of",
        "Vietnam": "Viet Nam",
        "Laos": "Lao People's Democratic Republic",
        "Iran": "Iran, Islamic Republic of",
        "Syria": "Syrian Arab Republic",
        "Tanzania": "Tanzania, United Republic of",
        "Venezuela": "Venezuela, Bolivarian Republic of",
        "Bolivia": "Bolivia, Plurinational State of",
        "Congo (Kinshasa)": "Congo, Democratic Republic of the",
        "Congo (Brazzaville)": "Congo",
    }

    return replacements.get(name, name)
