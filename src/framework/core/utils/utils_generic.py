"""Utility: Generic methods to be defined"""

from __future__ import annotations

import getpass
import os


def get_system_username():
    """
    Returns the current system username in a cross-platform way.
    Tries multiple methods for compatibility.
    """
    try:
        # Preferred method: works on most systems
        username = getpass.getuser()
        if username:
            return username
    except (OSError, KeyError):
        pass

    # Fallback: environment variables
    for env_var in ("USERNAME", "USER", "LOGNAME"):
        username = os.environ.get(env_var)
        if username:
            return username

    # If all methods fail
    return None


def get_worker_id() -> str:
    """Get the pytest-xdist worker ID or 'local' if not running in xdist.

    Returns:
        The worker ID string (e.g., 'gw0') or 'local' if not in xdist environment.
    """
    # pytest-xdist sets PYTEST_XDIST_WORKER like "gw0"
    return str(__import__("os").environ.get("PYTEST_XDIST_WORKER", "local"))

