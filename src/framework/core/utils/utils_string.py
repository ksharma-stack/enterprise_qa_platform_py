'''string utility stateless methods'''
from __future__ import annotations
import re

__all__ = ["to_snake_case", "to_camel_case", "is_palindrome"]

def to_snake_case(s: str) -> str:
    """Convert CamelCase or mixedCase to snake_case."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()

def to_camel_case(s: str) -> str:
    """Convert snake_case to camelCase."""
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def is_palindrome(s: str) -> bool:
    """Check if a string is a palindrome."""
    s = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    return s == s[::-1]