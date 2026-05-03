"""Exception classes"""


class FrameworkError(Exception):
    """Base exception for the automation framework."""


class ConfigError(FrameworkError):
    """Raised when configuration is missing or invalid."""


class ApiError(FrameworkError):
    """Raised when API calls fail in a framework-managed way."""
