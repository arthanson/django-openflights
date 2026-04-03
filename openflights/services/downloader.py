"""
File download service for OpenFlights data.

Downloads CSV/DAT files from OpenFlights distribution servers.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import requests
from tqdm import tqdm

from ..conf import DATA_URLS, FALLBACK_URLS, LOGGER_NAME, get_openflights_settings
from ..exceptions import DownloadError

logger = logging.getLogger(LOGGER_NAME)


class Downloader:
    """
    Service for downloading OpenFlights data files.

    Downloads and caches CSV data files.
    """

    def __init__(self, data_dir: str = None, force: bool = False, quiet: bool = False):
        """
        Initialize the downloader.

        Args:
            data_dir: Directory to store downloaded files
            force: If True, re-download even if file exists
            quiet: If True, suppress progress output
        """
        settings = get_openflights_settings()
        self.data_dir = Path(data_dir or settings.data_dir)
        self.force = force
        self.quiet = quiet
        self.timeout = settings.download_timeout
        self.max_size = settings.max_download_size

        # Ensure directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_file_path(self, data_type: str) -> Path:
        """
        Get the local path for a data file.

        Args:
            data_type: Type of data (airports, airlines, planes)

        Returns:
            Path to local file
        """
        filenames = {
            "airports": "airports-extended.dat",
            "airlines": "airlines.dat",
            "planes": "planes.dat",
        }
        filename = filenames.get(data_type, f"{data_type}.dat")
        return self.data_dir / filename

    def download(self, data_type: str) -> Path:
        """
        Download a data file.

        Args:
            data_type: Type of data to download

        Returns:
            Path to downloaded file

        Raises:
            DownloadError: If download fails
        """
        file_path = self.get_file_path(data_type)

        # Check if already downloaded
        if file_path.exists() and not self.force:
            logger.info("Using cached file: %s", file_path)
            return file_path

        # Get URLs
        primary_url = DATA_URLS.get(data_type)
        fallback_url = FALLBACK_URLS.get(data_type)

        if not primary_url:
            raise DownloadError(f"Unknown data type: {data_type}")

        # Try primary URL first
        logger.info("Downloading %s data...", data_type)
        try:
            self._download_file(primary_url, file_path)
            return file_path
        except DownloadError as e:
            logger.warning("Primary URL failed: %s", e)

            # Try fallback URL
            if fallback_url:
                logger.info("Trying fallback URL...")
                try:
                    self._download_file(fallback_url, file_path)
                    return file_path
                except DownloadError:
                    pass

            raise DownloadError(f"Failed to download {data_type} data")

    def _download_file(self, url: str, dest: Path) -> None:
        """
        Download a file with progress tracking.

        Args:
            url: URL to download
            dest: Destination path

        Raises:
            DownloadError: If download fails
        """
        try:
            response = requests.get(
                url,
                stream=True,
                timeout=self.timeout,
                headers={"User-Agent": "django-openflights/0.1"},
            )
            response.raise_for_status()

            # Check content length
            total_size = int(response.headers.get("content-length", 0))
            if total_size > self.max_size:
                raise DownloadError(
                    f"File too large: {total_size} bytes (max {self.max_size})"
                )

            # Download with progress bar
            with open(dest, "wb") as f:
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=dest.name,
                    disable=self.quiet,
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            logger.info("Downloaded: %s", dest)

        except requests.RequestException as e:
            # Cleanup partial download
            if dest.exists():
                dest.unlink()
            raise DownloadError(f"HTTP error downloading {url}: {e}") from e

    def download_all(self) -> dict:
        """
        Download all data files.

        Returns:
            Dict mapping data type to file path
        """
        paths = {}
        for data_type in DATA_URLS:
            try:
                paths[data_type] = self.download(data_type)
            except DownloadError as e:
                logger.error("Failed to download %s: %s", data_type, e)
        return paths

    def list_cached(self) -> list:
        """
        List cached data files.

        Returns:
            List of (data_type, path) tuples
        """
        cached = []
        for data_type in DATA_URLS:
            path = self.get_file_path(data_type)
            if path.exists():
                cached.append((data_type, path))
        return cached

    def clear_cache(self, data_type: str = None) -> None:
        """
        Clear cached files.

        Args:
            data_type: Specific type to clear, or None to clear all
        """
        if data_type:
            path = self.get_file_path(data_type)
            if path.exists():
                path.unlink()
                logger.info("Removed cached file: %s", path)
        else:
            for dt in DATA_URLS:
                path = self.get_file_path(dt)
                if path.exists():
                    path.unlink()
                    logger.info("Removed cached file: %s", path)
