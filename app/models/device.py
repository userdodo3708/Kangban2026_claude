"""Device model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.room import Room


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'disabled', 'revoked')",
            name="status_valid",
        ),
        Index("ix_devices_room_id", "room_id"),
        Index("ix_devices_status", "status"),
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.room_id", ondelete="RESTRICT"),
        nullable=False,
    )
    device_jwt: Mapped[str] = mapped_column(
        String(1024), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'active'")
    )

    room: Mapped[Room] = relationship("Room", back_populates="devices")
