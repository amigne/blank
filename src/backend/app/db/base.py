"""SQLAlchemy declarative base — shared by all model modules.

Imports are deferred so that ``Base.metadata`` is fully populated after
all model modules have been imported by ``app.models``.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""