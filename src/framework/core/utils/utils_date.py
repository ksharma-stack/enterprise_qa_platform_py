"""date time utility stateless methods"""

from datetime import datetime, timedelta

__all__ = ["days_between", "add_days", "current_timestamp"]


def days_between(date1: str, date2: str, fmt: str = "%Y-%m-%d") -> int:
    """Return the number of days between two dates."""
    d1 = datetime.strptime(date1, fmt)
    d2 = datetime.strptime(date2, fmt)
    return abs((d2 - d1).days)


def add_days(date_str: str, days: int, fmt: str = "%Y-%m-%d") -> str:
    """Add days to a date string."""
    date_obj = datetime.strptime(date_str, fmt)
    return (date_obj + timedelta(days=days)).strftime(fmt)


def current_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current timestamp as a string."""
    return datetime.now().strftime(fmt)

