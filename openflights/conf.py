"""
Configuration for OpenFlights data import.

Settings can be overridden in Django settings using the OPENFLIGHTS_ prefix.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings as django_settings

# Logger name for all OpenFlights operations
LOGGER_NAME = "openflights"

# OpenFlights data URLs
# Note: Route data is not included as OpenFlights no longer maintains route information.
DATA_URLS = {
    "airports": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports-extended.dat",
    "airlines": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat",
    "planes": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/planes.dat",
}

# Alternative URLs (fallback)
FALLBACK_URLS = {
    "airports": "https://openflights.org/data/airports-extended.dat",
    "airlines": "https://openflights.org/data/airlines.dat",
    "planes": "https://openflights.org/data/planes.dat",
}

# Field definitions for CSV parsing
# airports-extended.dat format
AIRPORT_FIELDS = [
    "openflights_id",
    "name",
    "city",
    "country",
    "iata",
    "icao",
    "latitude",
    "longitude",
    "altitude",
    "timezone_offset",
    "dst",
    "timezone",
    "type",
    "source",
]

# airlines.dat format
AIRLINE_FIELDS = [
    "openflights_id",
    "name",
    "alias",
    "iata",
    "icao",
    "callsign",
    "country",
    "active",
]

# planes.dat format
PLANE_FIELDS = [
    "name",
    "iata",
    "icao",
]

# Hub types from OpenFlights
HUB_TYPES = {
    "airport": "Airport",
    "station": "TrainStation",
    "port": "Port",
    "unknown": "Airport",  # Default to airport for unknown types
}

# Import options
# Note: Route data is not available as OpenFlights no longer maintains it.
IMPORT_OPTS = ["all", "airport", "airline", "plane"]
IMPORT_OPTS_ALL = ["airport", "airline", "plane"]

# Flush options
FLUSH_OPTS = ["all", "airport", "airline", "plane"]
FLUSH_OPTS_ALL = ["airport", "airline", "plane"]

# DST codes mapping
DST_CODES = {
    "E": "Europe",
    "A": "US/Canada",
    "S": "South America",
    "O": "Australia",
    "Z": "New Zealand",
    "N": "None",
    "U": "Unknown",
}

# Feet to meters conversion
FEET_TO_METERS = 0.3048


@dataclass
class OpenFlightsSettings:
    """Configuration settings for OpenFlights import operations."""

    # Directory for downloaded data
    data_dir: str = ""

    # What to import by default
    import_airports: bool = True
    import_airlines: bool = True
    import_planes: bool = True

    # Whether to import geometry
    import_geometry: bool = True

    # HTTP download timeout in seconds
    download_timeout: int = 120

    # Maximum download size in bytes (default 50MB)
    max_download_size: int = 50 * 1024 * 1024

    # Batch size for bulk operations
    batch_size: int = 1000

    # Plugin classes to load
    plugins: list = field(default_factory=list)

    # Link to django-cities models if available
    link_cities: bool = True


def get_settings() -> OpenFlightsSettings:
    """
    Create settings object from Django settings.

    Reads settings with OPENFLIGHTS_ prefix from Django settings.
    """
    # Default data directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    default_data_dir = os.path.join(app_dir, "data")

    settings_obj = OpenFlightsSettings(
        data_dir=getattr(django_settings, "OPENFLIGHTS_DATA_DIR", default_data_dir),
        import_airports=getattr(django_settings, "OPENFLIGHTS_IMPORT_AIRPORTS", True),
        import_airlines=getattr(django_settings, "OPENFLIGHTS_IMPORT_AIRLINES", True),
        import_planes=getattr(django_settings, "OPENFLIGHTS_IMPORT_PLANES", True),
        import_geometry=getattr(django_settings, "OPENFLIGHTS_IMPORT_GEOMETRY", True),
        download_timeout=getattr(django_settings, "OPENFLIGHTS_DOWNLOAD_TIMEOUT", 120),
        max_download_size=getattr(
            django_settings, "OPENFLIGHTS_MAX_DOWNLOAD_SIZE", 50 * 1024 * 1024
        ),
        batch_size=getattr(django_settings, "OPENFLIGHTS_BATCH_SIZE", 1000),
        plugins=getattr(django_settings, "OPENFLIGHTS_PLUGINS", []),
        link_cities=getattr(django_settings, "OPENFLIGHTS_LINK_CITIES", True),
    )

    # Ensure data directory exists
    os.makedirs(settings_obj.data_dir, exist_ok=True)

    return settings_obj


# Singleton settings instance
_settings: Optional[OpenFlightsSettings] = None


def get_openflights_settings() -> OpenFlightsSettings:
    """Get or create the singleton settings instance."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None
