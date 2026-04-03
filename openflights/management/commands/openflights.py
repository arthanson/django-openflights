"""
Management command to download and import OpenFlights data.

Usage:
    python manage.py openflights --import=all
    python manage.py openflights --import=airport,airline
    python manage.py openflights --flush=all --import=all
    python manage.py openflights --download-only
"""

import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from openflights.conf import (
    FLUSH_OPTS,
    FLUSH_OPTS_ALL,
    IMPORT_OPTS,
    IMPORT_OPTS_ALL,
    LOGGER_NAME,
    get_openflights_settings,
)
from openflights.importer import (
    AirlineImporter,
    AirportImporter,
    PlaneImporter,
)
from openflights.models import Aircraft, Airline, Airport, Port, TrainStation
from openflights.services import Downloader

logger = logging.getLogger(LOGGER_NAME)


class Command(BaseCommand):
    help = "Download and import OpenFlights aviation data"

    # Importer mapping
    IMPORTERS = {
        "airport": AirportImporter,
        "airline": AirlineImporter,
        "plane": PlaneImporter,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--import",
            type=str,
            default="",
            dest="import_type",
            help=f"What to import: {', '.join(IMPORT_OPTS)} (comma-separated)",
        )
        parser.add_argument(
            "--flush",
            type=str,
            default="",
            help=f"Delete existing data before import: {', '.join(FLUSH_OPTS)}",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-download of data files",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress progress output",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse data without saving to database",
        )
        parser.add_argument(
            "--download-only",
            action="store_true",
            help="Only download data files, don't import",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            dest="list_cached",
            help="List cached data files",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear cached downloads",
        )

    def handle(self, *args, **options):
        settings = get_openflights_settings()
        downloader = Downloader(
            data_dir=settings.data_dir,
            force=options["force"],
            quiet=options["quiet"],
        )

        # Handle --list
        if options["list_cached"]:
            self._list_cached(downloader)
            return

        # Handle --clear
        if options["clear"]:
            downloader.clear_cache()
            self.stdout.write("Cleared all cached downloads")
            return

        # Handle --download-only
        if options["download_only"]:
            self._download_all(downloader)
            return

        # Parse import types
        import_type = options["import_type"]
        flush_type = options["flush"]

        if not import_type and not flush_type:
            self.stdout.write(
                self.style.WARNING(
                    "No action specified. Use --import=all to import data, "
                    "or --help for more options."
                )
            )
            return

        # Handle flush
        if flush_type:
            self._handle_flush(flush_type)

        # Handle import
        if import_type:
            self._handle_import(import_type, options)

    def _list_cached(self, downloader: Downloader):
        """List cached data files."""
        cached = downloader.list_cached()

        if not cached:
            self.stdout.write("No cached data files found.")
            return

        self.stdout.write("Cached data files:")
        for data_type, path in cached:
            size = path.stat().st_size / 1024  # KB
            self.stdout.write(f"  {data_type}: {path} ({size:.1f} KB)")

    def _download_all(self, downloader: Downloader):
        """Download all data files."""
        self.stdout.write("Downloading all OpenFlights data files...")
        paths = downloader.download_all()

        for data_type, path in paths.items():
            self.stdout.write(
                self.style.SUCCESS(f"  {data_type}: {path}")
            )

    def _handle_flush(self, flush_type: str):
        """Delete existing data."""
        flush_types = [f.strip() for f in flush_type.split(",") if f.strip()]

        for ft in flush_types:
            if ft not in FLUSH_OPTS:
                raise CommandError(f"Invalid flush type: {ft}")

        if "all" in flush_types:
            flush_targets = FLUSH_OPTS_ALL
        else:
            flush_targets = flush_types

        for target in flush_targets:
            self._flush(target)

    def _flush(self, target: str):
        """Flush a specific target."""
        self.stdout.write(f"Flushing {target}...")

        if target == "airport":
            count = Airport.objects.all().delete()[0]
            count += TrainStation.objects.all().delete()[0]
            count += Port.objects.all().delete()[0]
            self.stdout.write(f"  Deleted {count} transport hubs")
        elif target == "airline":
            count = Airline.objects.all().delete()[0]
            self.stdout.write(f"  Deleted {count} airlines")
        elif target == "plane":
            count = Aircraft.objects.all().delete()[0]
            self.stdout.write(f"  Deleted {count} aircraft")

    def _handle_import(self, import_type: str, options: dict):
        """Run import operations."""
        import_types = [t.strip() for t in import_type.split(",") if t.strip()]

        for it in import_types:
            if it not in IMPORT_OPTS:
                raise CommandError(f"Invalid import type: {it}")

        if "all" in import_types:
            import_targets = IMPORT_OPTS_ALL
        else:
            import_targets = import_types

        total_stats = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        # Import in correct order
        ordered_targets = []
        for t in ["airport", "airline", "plane"]:
            if t in import_targets:
                ordered_targets.append(t)

        for target in ordered_targets:
            self._run_importer(target, options, total_stats)

        # Print summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import complete!"))
        self.stdout.write(f"  Processed: {total_stats['processed']}")
        self.stdout.write(f"  Created:   {total_stats['created']}")
        self.stdout.write(f"  Updated:   {total_stats['updated']}")
        self.stdout.write(f"  Skipped:   {total_stats['skipped']}")
        if total_stats["errors"]:
            self.stdout.write(
                self.style.WARNING(f"  Errors:    {total_stats['errors']}")
            )

    def _run_importer(self, target: str, options: dict, total_stats: dict):
        """Run a specific importer."""
        importer_class = self.IMPORTERS.get(target)
        if not importer_class:
            self.stdout.write(
                self.style.WARNING(f"No importer for: {target}")
            )
            return

        self.stdout.write(f"Importing {target}...")

        try:
            importer = importer_class(self, options)
            stats = importer.run()

            # Accumulate stats
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

        except Exception as e:
            logger.error("Import failed: %s", e, exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"Import failed: {e}")
            )
            raise CommandError(f"Import failed: {e}") from e
