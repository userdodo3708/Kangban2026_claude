"""Minimal table placeholders for the seven remaining main tables.

Only primary keys are defined here. Business fields must be added by new
Alembic revisions; do not edit the initial migrations once applied.
"""

from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MemoryChunk(Base):
    __tablename__ = "memory_chunks"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class MedicationPlan(Base):
    __tablename__ = "medication_plans"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class MediaLibraryItem(Base):
    __tablename__ = "media_library"

    media_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class HealthRecord(Base):
    __tablename__ = "health_records"

    record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class Voiceprint(Base):
    __tablename__ = "voiceprints"

    elder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class Conversation(Base):
    __tablename__ = "conversations"

    thread_id: Mapped[str] = mapped_column(String(128), primary_key=True)
