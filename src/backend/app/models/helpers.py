"""Normalisation helpers for case-insensitive uniqueness.

Unicode NFC + lowercase canonicalisation, used for:
- ``communities.normalized_name``
- ``users.normalized_email``
- ``memberships.normalized_username``
"""

import unicodedata


def normalize_identity(value: str) -> str:
    """Return the lowercase NFC-normalized form of *value*.

    This is the canonical representation used for all uniqueness
    constraints.
    """
    return unicodedata.normalize("NFC", value).lower()