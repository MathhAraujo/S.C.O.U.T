"""Create initial schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-07 21:35:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "athletes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("team", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_uid", sa.String(length=255), nullable=False),
        sa.Column("firmware_version", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_uid"),
    )
    op.create_index("ix_devices_device_uid", "devices", ["device_uid"])
    op.create_table(
        "device_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_id", sa.Uuid(), nullable=False),
        sa.Column("athlete_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_device_assignments_device_id", "device_assignments", ["device_id"])
    op.create_index("ix_device_assignments_athlete_id", "device_assignments", ["athlete_id"])
    op.create_index("ix_device_assignments_started_at", "device_assignments", ["started_at"])
    op.create_index("ix_device_assignments_ended_at", "device_assignments", ["ended_at"])
    op.create_index(
        "ux_device_assignments_active_device",
        "device_assignments",
        ["device_id"],
        unique=True,
        postgresql_where=sa.text("ended_at IS NULL"),
    )
    op.create_table(
        "temperature_measurements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_id", sa.Uuid(), nullable=False),
        sa.Column("athlete_id", sa.Uuid(), nullable=True),
        sa.Column("sensor", sa.String(length=50), nullable=False),
        sa.Column("value_celsius", sa.Numeric(5, 2), nullable=False),
        sa.Column("unit", sa.String(length=20), server_default="celsius", nullable=False),
        sa.Column("uptime_ms", sa.BigInteger(), nullable=True),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_temperature_measurements_device_id", "temperature_measurements", ["device_id"])
    op.create_index("ix_temperature_measurements_athlete_id", "temperature_measurements", ["athlete_id"])
    op.create_index("ix_temperature_measurements_received_at", "temperature_measurements", ["received_at"])
    op.create_index(
        "ix_temperature_measurements_device_received_at",
        "temperature_measurements",
        ["device_id", "received_at"],
    )
    op.create_index(
        "ix_temperature_measurements_athlete_received_at",
        "temperature_measurements",
        ["athlete_id", "received_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_temperature_measurements_athlete_received_at", table_name="temperature_measurements")
    op.drop_index("ix_temperature_measurements_device_received_at", table_name="temperature_measurements")
    op.drop_index("ix_temperature_measurements_received_at", table_name="temperature_measurements")
    op.drop_index("ix_temperature_measurements_athlete_id", table_name="temperature_measurements")
    op.drop_index("ix_temperature_measurements_device_id", table_name="temperature_measurements")
    op.drop_table("temperature_measurements")
    op.drop_index("ux_device_assignments_active_device", table_name="device_assignments")
    op.drop_index("ix_device_assignments_ended_at", table_name="device_assignments")
    op.drop_index("ix_device_assignments_started_at", table_name="device_assignments")
    op.drop_index("ix_device_assignments_athlete_id", table_name="device_assignments")
    op.drop_index("ix_device_assignments_device_id", table_name="device_assignments")
    op.drop_table("device_assignments")
    op.drop_index("ix_devices_device_uid", table_name="devices")
    op.drop_table("devices")
    op.drop_table("athletes")
