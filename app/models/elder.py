"""Elder model."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.persona import Persona


class Elder(Base):
    __tablename__ = "elders"
    __table_args__ = (
        CheckConstraint(
            "gender IN ('male', 'female', 'other', 'unknown')",
            name="gender_valid",
        ),
        CheckConstraint(
            "status IN ('active', 'checked_out', 'inactive')",
            name="status_valid",
        ),
        Index("ix_elders_persona_id", "persona_id"),
        Index("ix_elders_status", "status"),
    )

    elder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    persona_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personas.persona_id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'active'")
    )

    persona: Mapped[Persona | None] = relationship(
        "Persona", back_populates="elders"
    )
