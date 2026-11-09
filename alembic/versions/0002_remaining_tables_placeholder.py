"""create primary-key-only placeholders for the remaining seven tables

Revision ID: 0002_remaining_tables
Revises: 0001_core_schema
Create Date: 2026-11-08

No business fields are defined here by design. Add them in later revisions;
never edit this file after it has been applied.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_remaining_tables"
down_revision: Union[str, None] = "0001_core_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "memory_chunks",
        sa.Column("chunk_id", UUID, nullable=False),
        sa.PrimaryKeyConstraint("chunk_id", name="pk_memory_chunks"),
        comment="占位表：业务字段由后续迁移添加",
    )
    op.create_table(
        "medication_plans",
        sa.Column("plan_id", UUID, nullable=False),
        sa.PrimaryKeyConstraint("plan_id", name="pk_medication_plans"),
        comment="占位表：业务字段由后续迁移添加",
    )
    op.create_table(
        "media_library",
        sa.Column("media_id", UUID, nullable=False),
        sa.PrimaryKeyConstraint("media_id", name="pk_media_library"),
        comment="占位表：业务字段由后续迁移添加",
    )
    op.create_table(
        "health_records",
        sa.Column("record_id", UUID, nullable=False),
        sa.PrimaryKeyConstraint("record_id", name="pk_health_records"),
        comment="占位表：业务字段由后续迁移添加",
    )
    op.create_table(
        "voiceprints",
        sa.Column("elder_id", UUID, nullable=False),
        sa.PrimaryKeyConstraint("elder_id", name="pk_voiceprints"),
        comment="占位表：业务字段由后续迁移添加",
    )
    op.create_table(
        "work_orders",
        sa.Column("order_id", UUID, nullable=False),
        sa.PrimaryKeyConstraint("order_id", name="pk_work_orders"),
        comment="占位表：业务字段由后续迁移添加",
    )
    op.create_table(
        "conversations",
        sa.Column("thread_id", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("thread_id", name="pk_conversations"),
        comment="占位表：业务字段由后续迁移添加",
    )


def downgrade() -> None:
    op.drop_table("conversations")
    op.drop_table("work_orders")
    op.drop_table("voiceprints")
    op.drop_table("health_records")
    op.drop_table("media_library")
    op.drop_table("medication_plans")
    op.drop_table("memory_chunks")
