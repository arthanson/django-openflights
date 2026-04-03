"""
Airport importer for OpenFlights data.

Handles airports, train stations, and ports based on the 'type' field.
"""

import logging
from typing import Any, Optional, Tuple

from django.contrib.gis.geos import Point
from django.db import transaction

from ..conf import HUB_TYPES, LOGGER_NAME, get_openflights_settings
from ..exceptions import ValidationError
from ..models import Airport, Port, TrainStation
from ..util import parse_float, parse_int, parse_openflights_null, slugify
from .base import BaseImporter

logger = logging.getLogger(LOGGER_NAME)


class AirportImporter(BaseImporter):
    """
    Importer for airports, train stations, and ports.

    The OpenFlights airports-extended.dat file contains all three types,
    differentiated by the 'type' field.
    """

    data_type = "airports"

    def __init__(self, command, options: dict):
        super().__init__(command, options)

        # Track existing IDs for each model
        self.existing_airport_ids = set()
        self.existing_station_ids = set()
        self.existing_port_ids = set()

    def get_model_class(self) -> type:
        return Airport

    def build_indices(self) -> None:
        """Build indices of existing records."""
        self.existing_airport_ids = set(
            Airport.objects.values_list("openflights_id", flat=True)
        )
        self.existing_station_ids = set(
            TrainStation.objects.values_list("openflights_id", flat=True)
        )
        self.existing_port_ids = set(
            Port.objects.values_list("openflights_id", flat=True)
        )
        logger.info(
            "Found %d airports, %d stations, %d ports in database",
            len(self.existing_airport_ids),
            len(self.existing_station_ids),
            len(self.existing_port_ids),
        )

    def parse_item(self, item: dict) -> Optional[dict]:
        """
        Parse an airport/station/port record.

        Args:
            item: Raw record from CSV

        Returns:
            Parsed dict or None to skip
        """
        settings = get_openflights_settings()

        # Parse OpenFlights ID
        openflights_id = self.validator.parse_openflights_id(
            item.get("openflights_id"),
            required=True,
        )
        if openflights_id is None:
            return None

        # Get name
        name = parse_openflights_null(item.get("name"))
        if not name:
            return None

        # Determine hub type
        hub_type = parse_openflights_null(item.get("type")) or "airport"
        hub_type = hub_type.lower()
        model_name = HUB_TYPES.get(hub_type, "Airport")

        # Parse codes
        iata = self.validator.parse_iata(item.get("iata"))
        icao = self.validator.parse_icao(item.get("icao"))

        # Parse location
        latitude = parse_float(item.get("latitude"))
        longitude = parse_float(item.get("longitude"))

        location = None
        if settings.import_geometry and latitude is not None and longitude is not None:
            location = self.validator.parse_coordinates(
                latitude, longitude, f"{model_name} {name}"
            )

        # Parse altitude (convert from feet to meters)
        altitude = self.validator.parse_altitude(item.get("altitude"), in_feet=True)

        # Parse timezone
        timezone = parse_openflights_null(item.get("timezone")) or ""
        timezone_offset = self.validator.parse_timezone_offset(item.get("timezone_offset"))
        dst = parse_openflights_null(item.get("dst")) or ""

        # Location info
        city_name = parse_openflights_null(item.get("city")) or ""
        country_name = parse_openflights_null(item.get("country")) or ""

        # Source
        source = parse_openflights_null(item.get("source")) or ""

        # Generate slug
        slug = slugify(name)
        if iata:
            slug = f"{slug}-{iata.lower()}" if slug else iata.lower()
        elif slug:
            slug = f"{slug}-{openflights_id}"
        else:
            slug = str(openflights_id)

        return {
            "openflights_id": openflights_id,
            "model_name": model_name,
            "name": name[:200],
            "slug": slug[:200],
            "iata": iata,
            "icao": icao,
            "city_name": city_name[:100],
            "country_name": country_name[:100],
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "timezone": timezone[:50],
            "timezone_offset": timezone_offset,
            "dst": dst[:1],
            "source": source[:50],
        }

    @transaction.atomic
    def create_or_update(self, parsed: dict) -> Tuple[Any, bool]:
        """
        Create or update an airport/station/port record.

        Args:
            parsed: Parsed data dict

        Returns:
            Tuple of (model instance, created boolean)
        """
        openflights_id = parsed.pop("openflights_id")
        model_name = parsed.pop("model_name")
        location = parsed.pop("location", None)

        # Select model and existing ID set
        if model_name == "TrainStation":
            model_class = TrainStation
            existing_ids = self.existing_station_ids
        elif model_name == "Port":
            model_class = Port
            existing_ids = self.existing_port_ids
        else:
            model_class = Airport
            existing_ids = self.existing_airport_ids

        # Check if exists
        is_new = openflights_id not in existing_ids

        if is_new:
            # Create new record
            obj = model_class(openflights_id=openflights_id, **parsed)
            if location:
                obj.location = location
            obj.save()
            existing_ids.add(openflights_id)
            created = True
        else:
            # Update existing
            obj, created = model_class.objects.update_or_create(
                openflights_id=openflights_id,
                defaults=parsed,
            )
            # Update location separately
            if location:
                obj.location = location
                obj.save(update_fields=["location"])

        return obj, created
