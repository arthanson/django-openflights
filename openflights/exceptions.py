"""Custom exceptions for OpenFlights import operations."""


class OpenFlightsException(Exception):
    """Base exception for OpenFlights operations."""

    pass


class ValidationError(OpenFlightsException):
    """Raised when data validation fails during import."""

    pass


class DownloadError(OpenFlightsException):
    """Raised when file download fails."""

    pass


class ParseError(OpenFlightsException):
    """Raised when data parsing fails."""

    pass


class HookException(OpenFlightsException):
    """Raise in plugin hooks to skip the current item."""

    pass
