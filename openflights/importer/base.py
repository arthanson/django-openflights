"""
Base importer class for OpenFlights data.

Implements the template method pattern for import operations.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

from django.db import models, transaction
from tqdm import tqdm

from ..conf import LOGGER_NAME, get_openflights_settings
from ..exceptions import HookException, ValidationError
from ..services import CSVParser, Downloader, Validator

logger = logging.getLogger(LOGGER_NAME)


class BaseImporter(ABC):
    """
    Abstract base class for OpenFlights data importers.

    Implements the template method pattern with the following workflow:
    1. download_data() - Download data file
    2. build_indices() - Build lookup indices
    3. import_records() - Import records with progress
    4. cleanup() - Post-import processing
    """

    # Data type for this importer (airports, airlines, planes)
    data_type: str = None

    def __init__(self, command, options: dict):
        """
        Initialize the importer.

        Args:
            command: Django management command instance
            options: Command options dict
        """
        self.command = command
        self.options = options
        self.settings = get_openflights_settings()

        # Extract common options
        self.force = options.get("force", False)
        self.quiet = options.get("quiet", False)
        self.dry_run = options.get("dry_run", False)

        # Initialize services
        self.downloader = Downloader(
            data_dir=self.settings.data_dir,
            force=self.force,
            quiet=self.quiet,
        )
        self.validator = Validator()

        # Statistics
        self.stats = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        # Plugin hooks
        self.plugins = self._load_plugins()

    def _load_plugins(self) -> list:
        """Load plugin classes from settings."""
        plugins = []
        for plugin_path in self.settings.plugins:
            try:
                module_path, class_name = plugin_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                plugin_class = getattr(module, class_name)
                plugins.append(plugin_class())
                logger.info("Loaded plugin: %s", plugin_path)
            except Exception as e:
                logger.warning("Failed to load plugin %s: %s", plugin_path, e)
        return plugins

    def run(self) -> dict:
        """
        Execute the import workflow.

        Returns:
            Statistics dict
        """
        logger.info("Starting %s import", self.get_description())

        try:
            # Step 1: Download data
            file_path = self.download_data()

            # Step 2: Build indices
            self.build_indices()

            # Step 3: Import records
            self._import_from_file(file_path)

            # Step 4: Cleanup
            self.cleanup()

        except Exception as e:
            logger.error("Import failed: %s", e, exc_info=True)
            raise

        logger.info(
            "Import complete: %d processed, %d created, %d updated, %d skipped, %d errors",
            self.stats["processed"],
            self.stats["created"],
            self.stats["updated"],
            self.stats["skipped"],
            self.stats["errors"],
        )

        return self.stats

    def download_data(self) -> Path:
        """
        Download data file.

        Returns:
            Path to downloaded file
        """
        return self.downloader.download(self.data_type)

    def _import_from_file(self, file_path: Path) -> None:
        """
        Import records from a data file.

        Args:
            file_path: Path to data file
        """
        parser = CSVParser(file_path, self.data_type, quiet=self.quiet)

        # Get count for progress bar
        total = parser.count_records()
        logger.info("Found %d records to process", total)

        # Iterate with progress bar
        with tqdm(
            total=total,
            desc=self.get_description(),
            disable=self.quiet,
        ) as pbar:
            for item in parser.iter_records():
                self._process_item(item)
                pbar.update(1)

    def _process_item(self, item: dict) -> None:
        """
        Process a single data item.

        Args:
            item: Parsed record dict
        """
        self.stats["processed"] += 1

        try:
            # Pre-processing hook
            if not self._call_hook("pre", item):
                self.stats["skipped"] += 1
                return

            # Parse item
            parsed = self.parse_item(item)
            if parsed is None:
                self.stats["skipped"] += 1
                return

            # Create or update (skip if dry run)
            if self.dry_run:
                logger.debug("Dry run: would import %s", parsed.get("name", ""))
                return

            obj, created = self.create_or_update(parsed)

            if created:
                self.stats["created"] += 1
            else:
                self.stats["updated"] += 1

            # Post-processing hook
            self._call_hook("post", obj, item)

        except ValidationError as e:
            logger.debug("Validation error: %s", e)
            self.stats["skipped"] += 1

        except Exception as e:
            logger.error("Error processing item: %s", e, exc_info=True)
            self.stats["errors"] += 1

    def _call_hook(self, hook_type: str, *args) -> bool:
        """
        Call plugin hooks.

        Args:
            hook_type: "pre" or "post"
            *args: Arguments to pass to hook

        Returns:
            True to continue processing, False to skip
        """
        hook_name = f"{self.get_hook_prefix()}_{hook_type}"

        for plugin in self.plugins:
            hook = getattr(plugin, hook_name, None)
            if hook:
                try:
                    hook(self.command, *args)
                except HookException:
                    return False
                except Exception as e:
                    logger.warning(
                        "Plugin hook %s.%s failed: %s",
                        plugin.__class__.__name__,
                        hook_name,
                        e,
                    )

        return True

    def build_indices(self) -> None:
        """Build lookup indices before import."""
        pass

    def cleanup(self) -> None:
        """Post-import cleanup."""
        pass

    def get_description(self) -> str:
        """Get description for progress display."""
        model = self.get_model_class()
        return f"Importing {model._meta.verbose_name_plural}"

    def get_hook_prefix(self) -> str:
        """Get prefix for hook method names."""
        model = self.get_model_class()
        return model._meta.model_name

    @abstractmethod
    def get_model_class(self) -> type:
        """Return the Django model class to import."""
        pass

    @abstractmethod
    def parse_item(self, item: dict) -> Optional[dict]:
        """Parse a raw data item into model fields."""
        pass

    @abstractmethod
    def create_or_update(self, parsed: dict) -> Tuple[models.Model, bool]:
        """Create or update a database record."""
        pass
