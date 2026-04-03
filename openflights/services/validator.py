"""
Data validation service for OpenFlights import operations.
"""

import logging
from typing import Any, Optional

from django.contrib.gis.geos import Point

from ..conf import LOGGER_NAME
from ..exceptions import ValidationError
from ..util import (
    clean_iata_code,
    clean_icao_code,
    feet_to_meters,
    parse_bool,
    parse_float,
    parse_int,
    parse_openflights_null,
)

logger = logging.getLogger(LOGGER_NAME)


class Validator:
    """
    Validation utilities for OpenFlights data import.

    Provides methods to parse and validate common data types.
    """

    def parse_openflights_id(
        self,
        value: Any,
        field_name: str = "openflights_id",
        required: bool = True,
    ) -> Optional[int]:
        """
        Parse an OpenFlights ID.

        Args:
            value: Value to parse
            field_name: Field name for error messages
            required: If True, raise error if value is invalid

        Returns:
            OpenFlights ID or None

        Raises:
            ValidationError: If required and value is invalid
        """
        parsed = parse_int(value)

        if parsed is None or parsed < 0:
            if required:
                raise ValidationError(f"{field_name}: valid OpenFlights ID required")
            return None

        return parsed

    def parse_coordinates(
        self,
        latitude: Any,
        longitude: Any,
        entity_type: str = "hub",
    ) -> Optional[Point]:
        """
        Parse latitude/longitude into a Point.

        Args:
            latitude: Latitude value
            longitude: Longitude value
            entity_type: Entity type for error messages

        Returns:
            Point geometry or None
        """
        lat = parse_float(latitude)
        lon = parse_float(longitude)

        if lat is None or lon is None:
            return None

        # Validate coordinate ranges
        if not -90 <= lat <= 90:
            logger.warning("%s: latitude out of range: %s", entity_type, lat)
            return None

        if not -180 <= lon <= 180:
            logger.warning("%s: longitude out of range: %s", entity_type, lon)
            return None

        try:
            return Point(lon, lat, srid=4326)
        except Exception as e:
            logger.warning(
                "%s: failed to create Point(%s, %s): %s",
                entity_type,
                lon,
                lat,
                e,
            )
            return None

    def parse_altitude(self, value: Any, in_feet: bool = True) -> float:
        """
        Parse altitude value.

        Args:
            value: Altitude value
            in_feet: If True, convert from feet to meters

        Returns:
            Altitude in meters
        """
        alt = parse_float(value, default=0.0)
        if in_feet and alt:
            alt = feet_to_meters(alt)
        return alt

    def parse_iata(self, value: Any) -> str:
        """
        Parse and validate IATA code.

        Args:
            value: Raw IATA code

        Returns:
            Cleaned IATA code or empty string
        """
        return clean_iata_code(value or "")

    def parse_icao(self, value: Any) -> str:
        """
        Parse and validate ICAO code.

        Args:
            value: Raw ICAO code

        Returns:
            Cleaned ICAO code or empty string
        """
        return clean_icao_code(value or "")

    def parse_timezone_offset(self, value: Any) -> Optional[float]:
        """
        Parse timezone offset.

        Args:
            value: Offset value

        Returns:
            Offset in hours or None
        """
        offset = parse_float(value)
        if offset is not None and not -12 <= offset <= 14:
            return None
        return offset

    def parse_active(self, value: Any) -> bool:
        """
        Parse active/operational status.

        Args:
            value: Active flag (Y/N)

        Returns:
            Boolean
        """
        return parse_bool(value, default=True)

    def parse_stops(self, value: Any) -> int:
        """
        Parse number of stops.

        Args:
            value: Stops value

        Returns:
            Number of stops (0 = direct)
        """
        stops = parse_int(value, default=0)
        return max(0, stops)

    def parse_codeshare(self, value: Any) -> bool:
        """
        Parse codeshare flag.

        OpenFlights uses 'Y' for codeshare.

        Args:
            value: Codeshare value

        Returns:
            Boolean
        """
        cleaned = parse_openflights_null(value)
        if cleaned and cleaned.upper() == "Y":
            return True
        return False

    def require_field(
        self,
        data: dict,
        field_name: str,
        entity_type: str = "record",
    ) -> Any:
        """
        Require a field to be present and non-empty.

        Args:
            data: Data dict to check
            field_name: Field name to require
            entity_type: Entity type for error messages

        Returns:
            Field value

        Raises:
            ValidationError: If field is missing or empty
        """
        value = data.get(field_name)
        if value is None or value == "":
            raise ValidationError(
                f"{entity_type}: required field '{field_name}' is missing or empty"
            )
        return value
