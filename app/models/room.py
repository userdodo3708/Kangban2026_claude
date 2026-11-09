"""Room model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, SmallInteger, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.elder import Elder


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        CheckConstraint("bed_count > 0", name="bed_count_positive"),
        Index("ix_rooms_occupant_ids", "occupant_ids", postgresql_using="gin"),
    )

    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    bed_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    occupant_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        server_default=text("'{}'::uuid[]"),
    )

    devices: Mapped[list[Device]] = relationship(
        "Device", back_populates="room", passive_deletes=True
    )
    occupants: Mapped[list[Elder]] = relationship(
        "Elder",
        primaryjoin="foreign(Elder.elder_id) == any_(Room.occupant_ids)",
        viewonly=True,
    )
