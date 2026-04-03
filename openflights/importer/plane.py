"""
Aircraft/Plane importer for OpenFlights data.
"""

import logging
from typing import Optional, Tuple

from django.db import transaction

from ..conf import LOGGER_NAME
from ..models import Aircraft
from ..util import parse_openflights_null, slugify
from .base import BaseImporter

logger = logging.getLogger(LOGGER_NAME)


class PlaneImporter(BaseImporter):
    """
    Importer for aircraft types.
    """

    data_type = "planes"

    def __init__(self, command, options: dict):
        super().__init__(command, options)
        self.existing_iata_codes = set()

    def get_model_class(self) -> type:
        return Aircraft

    def build_indices(self) -> None:
        """Build index of existing aircraft."""
        self.existing_iata_codes = set(
            Aircraft.objects.exclude(iata="").values_list("iata", flat=True)
        )
        logger.info("Found %d aircraft types in database", len(self.existing_iata_codes))

    def parse_item(self, item: dict) -> Optional[dict]:
        """
        Parse an aircraft record.

        Args:
            item: Raw record from CSV

        Returns:
            Parsed dict or None to skip
        """
        # Get name
        name = parse_openflights_null(item.get("name"))
        if not name:
            return None

        # Get codes
        iata = parse_openflights_null(item.get("iata")) or ""
        iata = iata.upper().strip()
        if not iata:
            return None  # IATA code is required for aircraft

        icao = parse_openflights_null(item.get("icao")) or ""
        icao = icao.upper().strip()

        # Skip duplicates
        if iata in self.existing_iata_codes:
            return None

        # Generate slug
        slug = slugify(name) or iata.lower()

        return {
            "name": name[:200],
            "slug": slug[:200],
            "iata": iata[:4],
            "icao": icao[:4],
        }

    @transaction.atomic
    def create_or_update(self, parsed: dict) -> Tuple[Aircraft, bool]:
        """
        Create an aircraft record.

        Args:
            parsed: Parsed data dict

        Returns:
            Tuple of (Aircraft instance, created boolean)
        """
        iata = parsed["iata"]

        aircraft = Aircraft.objects.create(**parsed)
        self.existing_iata_codes.add(iata)

        return aircraft, True
