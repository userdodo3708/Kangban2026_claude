"""Persona template model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.elder import Elder


class Persona(Base):
    __tablename__ = "personas"
    __table_args__ = (Index("ix_personas_voice_id", "voice_id"),)

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(512), nullable=False)
    personality: Mapped[str] = mapped_column(Text, nullable=False)
    greeting: Mapped[str] = mapped_column(Text, nullable=False)
    voice_id: Mapped[str] = mapped_column(String(64), nullable=False)

    elders: Mapped[list[Elder]] = relationship("Elder", back_populates="persona")
