"""Schema invariants for the Day 1 data model."""

from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers

from app.models import Base

CORE_COLUMNS = {
    "personas": {"persona_id", "name", "avatar_url", "personality", "greeting", "voice_id"},
    "rooms": {"room_id", "bed_count", "occupant_ids"},
    "elders": {"elder_id", "name", "birth_date", "gender", "persona_id", "status"},
    "devices": {"device_id", "room_id", "device_jwt", "status"},
}

PLACEHOLDER_TABLES = {
    "memory_chunks": "chunk_id",
    "medication_plans": "plan_id",
    "media_library": "media_id",
    "health_records": "record_id",
    "voiceprints": "elder_id",
    "work_orders": "order_id",
    "conversations": "thread_id",
}


def test_core_table_columns_match_spec():
    assert set(Base.metadata.tables) == set(CORE_COLUMNS) | set(PLACEHOLDER_TABLES)
    for table_name, expected in CORE_COLUMNS.items():
        actual = {column.name for column in Base.metadata.tables[table_name].columns}
        assert actual == expected, (table_name, actual)


def test_placeholder_tables_have_only_primary_keys():
    for table_name, primary_key in PLACEHOLDER_TABLES.items():
        table = Base.metadata.tables[table_name]
        assert {column.name for column in table.columns} == {primary_key}
        assert {column.name for column in table.primary_key.columns} == {primary_key}
        assert not table.foreign_key_constraints


def test_core_indexes_and_foreign_keys():
    assert "ix_personas_voice_id" in {index.name for index in Base.metadata.tables["personas"].indexes}
    room_indexes = {index.name: index for index in Base.metadata.tables["rooms"].indexes}
    assert room_indexes["ix_rooms_occupant_ids"].dialect_options["postgresql"]["using"] == "gin"
    assert {
        fk.elements[0].target_fullname
        for fk in Base.metadata.tables["elders"].foreign_key_constraints
    } == {"personas.persona_id"}
    assert {
        fk.elements[0].target_fullname
        for fk in Base.metadata.tables["devices"].foreign_key_constraints
    } == {"rooms.room_id"}


def test_relationships_configure():
    configure_mappers()
    from app.models import Device, Elder, Persona, Room

    assert "persona" in inspect(Elder).relationships
    assert "elders" in inspect(Persona).relationships
    assert "room" in inspect(Device).relationships
    assert "devices" in inspect(Room).relationships
    assert "occupants" in inspect(Room).relationships
