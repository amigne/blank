"""ORM models — imported here so Alembic autogenerate can detect them.

Import order matters for FK resolution: base tables first, then dependent tables.
"""

from app.models.user import User  # noqa: F401 — populate Base.metadata

__all__ = ["User"]
