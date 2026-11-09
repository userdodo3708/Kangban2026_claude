"""SQLAlchemy models.

Importing this package registers every model on ``Base.metadata`` so
Alembic and ``create_all`` see the full schema.
"""

from app.models.base import Base
from app.models.device import Device
from app.models.elder import Elder
from app.models.persona import Persona
from app.models.placeholder import (
    Conversation,
    HealthRecord,
    MediaLibraryItem,
    MedicationPlan,
    MemoryChunk,
    Voiceprint,
    WorkOrder,
)
from app.models.room import Room

__all__ = [
    "Base",
    "Conversation",
    "Device",
    "Elder",
    "HealthRecord",
    "MediaLibraryItem",
    "MedicationPlan",
    "MemoryChunk",
    "Persona",
    "Room",
    "Voiceprint",
    "WorkOrder",
]
