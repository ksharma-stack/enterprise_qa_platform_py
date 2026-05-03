"""file utility stateless methods"""

import os

__all__ = ["file_exists", "list_files", "read_file"]


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def list_files(directory: str) -> list:
    """List all files in a directory."""
    if not os.path.isdir(directory):
        raise ValueError(f"{directory} is not a valid directory")
    return [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]


def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read and return the contents of a file."""
    if not file_exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding=encoding) as f:
        return f.read()

