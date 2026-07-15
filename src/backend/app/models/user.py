"""User aggregate root — global account."""

from datetime import datetime, UTC
from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, validates
from uuid import UUID

from app.db.base import Base
from app.models.helpers import normalize_identity


class User(Base):
    __tablename__ = "users"
    __table_args__ = (

    )

    # ── Primary key ───────────────────────────────────────────────────
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    # ── Identity ───────────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        comment="User e-mail address",
    )
    normalized_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        comment="Lowercase canonical form of e-mail (used for uniqueness)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Password hash (Argon2id)",
    )

    # ── Preferences ────────────────────────────────────────────────────
    language: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="en",
        server_default=text("'en'"),
    )
    locale: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        default="en-US",
        server_default=text("'en-US'"),
    )

    # ── Timestamps ─────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("now()"),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Most recent successful login"
    )

    # ── Normalisation hooks ──────────────────────────────────────────────

    @validates("email")
    def _sync_normalized_email(self, _key: str, value: str | None) -> str | None:
        """Keep ``normalized_email`` in sync with ``email``."""
        # Bypass the ``normalized_email`` validator via __dict__ because
        # ``self.email`` still holds the *previous* value at this point.
        self.__dict__["normalized_email"] = normalize_identity(value) if value is not None else None
        return value

    @validates("normalized_email")
    def _force_normalized_email(self, _key: str, _value: str | None) -> str | None:
        """Always derive ``normalized_email`` from ``email`` — ignore explicit value."""
        return normalize_identity(self.email)