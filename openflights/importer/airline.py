"""
Airline importer for OpenFlights data.
"""

import logging
from typing import Optional, Tuple

from django.db import transaction

from ..conf import LOGGER_NAME
from ..models import Airline
from ..util import parse_openflights_null, slugify
from .base import BaseImporter

logger = logging.getLogger(LOGGER_NAME)


class AirlineImporter(BaseImporter):
    """
    Importer for airlines.
    """

    data_type = "airlines"

    def __init__(self, command, options: dict):
        super().__init__(command, options)
        self.existing_ids = set()

    def get_model_class(self) -> type:
        return Airline

    def build_indices(self) -> None:
        """Build index of existing airlines."""
        self.existing_ids = set(
            Airline.objects.values_list("openflights_id", flat=True)
        )
        logger.info("Found %d airlines in database", len(self.existing_ids))

    def parse_item(self, item: dict) -> Optional[dict]:
        """
        Parse an airline record.

        Args:
            item: Raw record from CSV

        Returns:
            Parsed dict or None to skip
        """
        # Parse OpenFlights ID
        openflights_id = self.validator.parse_openflights_id(
            item.get("openflights_id"),
            required=True,
        )
        if openflights_id is None:
            return None

        # Skip special entries (ID -1 is "Unknown", etc.)
        if openflights_id < 1:
            return None

        # Get name
        name = parse_openflights_null(item.get("name"))
        if not name:
            return None

        # Parse codes
        # Note: Airline IATA codes are 2 characters, ICAO are 3
        iata = parse_openflights_null(item.get("iata")) or ""
        iata = iata.upper().strip()
        if iata == "-" or len(iata) > 3:
            iata = ""

        icao = parse_openflights_null(item.get("icao")) or ""
        icao = icao.upper().strip()
        if len(icao) > 4:
            icao = ""

        # Other fields
        alias = parse_openflights_null(item.get("alias")) or ""
        callsign = parse_openflights_null(item.get("callsign")) or ""
        country_name = parse_openflights_null(item.get("country")) or ""

        # Parse active status
        is_active = self.validator.parse_active(item.get("active"))

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
            "name": name[:200],
            "alias": alias[:200],
            "slug": slug[:200],
            "iata": iata[:3],
            "icao": icao[:4],
            "callsign": callsign[:50],
            "country_name": country_name[:100],
            "is_active": is_active,
        }

    @transaction.atomic
    def create_or_update(self, parsed: dict) -> Tuple[Airline, bool]:
        """
        Create or update an airline record.

        Args:
            parsed: Parsed data dict

        Returns:
            Tuple of (Airline instance, created boolean)
        """
        openflights_id = parsed.pop("openflights_id")

        # Check if exists
        is_new = openflights_id not in self.existing_ids

        if is_new:
            airline = Airline.objects.create(
                openflights_id=openflights_id,
                **parsed,
            )
            self.existing_ids.add(openflights_id)
            created = True
        else:
            airline, created = Airline.objects.update_or_create(
                openflights_id=openflights_id,
                defaults=parsed,
            )

        return airline, created
