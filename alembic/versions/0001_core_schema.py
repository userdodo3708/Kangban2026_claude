"""create the four core tables: rooms, devices, elders, personas

Revision ID: 0001_core_schema
Revises:
Create Date: 2026-11-08

The column set is fixed by docs/02_技术规范.md section 九. Do not add
business columns to this revision; create a new revision instead.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_core_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "personas",
        sa.Column("persona_id", UUID, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=False),
        sa.Column("personality", sa.Text(), nullable=False),
        sa.Column("greeting", sa.Text(), nullable=False),
        sa.Column("voice_id", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("persona_id", name="pk_personas"),
        comment="人设模板；avatar_url 仅引用现成 VRM（B3）",
    )
    op.create_index("ix_personas_voice_id", "personas", ["voice_id"])

    op.create_table(
        "rooms",
        sa.Column("room_id", UUID, nullable=False),
        sa.Column("bed_count", sa.SmallInteger(), nullable=False),
        sa.Column(
            "occupant_ids",
            postgresql.ARRAY(UUID),
            nullable=False,
            server_default=sa.text("'{}'::uuid[]"),
        ),
        sa.CheckConstraint("bed_count > 0", name="bed_count_positive"),
        sa.PrimaryKeyConstraint("room_id", name="pk_rooms"),
        comment="房间信息；occupant_ids 由应用维护，数组元素无数据库外键",
    )
    op.create_index(
        "ix_rooms_occupant_ids",
        "rooms",
        ["occupant_ids"],
        postgresql_using="gin",
    )

    op.create_table(
        "elders",
        sa.Column("elder_id", UUID, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("persona_id", UUID, nullable=True),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.CheckConstraint(
            "gender IN ('male', 'female', 'other', 'unknown')",
            name="gender_valid",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'checked_out', 'inactive')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["persona_id"],
            ["personas.persona_id"],
            name="fk_elders_persona_id_personas",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("elder_id", name="pk_elders"),
        comment="长者档案；不含病历字段（B8）",
    )
    op.create_index("ix_elders_persona_id", "elders", ["persona_id"])
    op.create_index("ix_elders_status", "elders", ["status"])

    op.create_table(
        "devices",
        sa.Column("device_id", UUID, nullable=False),
        sa.Column("room_id", UUID, nullable=False),
        sa.Column("device_jwt", sa.String(length=1024), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled', 'revoked')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.room_id"],
            name="fk_devices_room_id_rooms",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("device_id", name="pk_devices"),
        sa.UniqueConstraint("device_jwt", name="uq_devices_device_jwt"),
        comment="平板设备与房间绑定；device_jwt 禁止写入日志",
    )
    op.create_index("ix_devices_room_id", "devices", ["room_id"])
    op.create_index("ix_devices_status", "devices", ["status"])


def downgrade() -> None:
    op.drop_index("ix_devices_status", table_name="devices")
    op.drop_index("ix_devices_room_id", table_name="devices")
    op.drop_table("devices")

    op.drop_index("ix_elders_status", table_name="elders")
    op.drop_index("ix_elders_persona_id", table_name="elders")
    op.drop_table("elders")

    op.drop_index("ix_rooms_occupant_ids", table_name="rooms")
    op.drop_table("rooms")

    op.drop_index("ix_personas_voice_id", table_name="personas")
    op.drop_table("personas")
