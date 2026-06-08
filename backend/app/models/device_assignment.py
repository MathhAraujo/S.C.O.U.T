import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DeviceAssignment(Base):
    __tablename__ = "device_assignments"
    __table_args__ = (
        Index("ix_device_assignments_device_id", "device_id"),
        Index("ix_device_assignments_athlete_id", "athlete_id"),
        Index("ix_device_assignments_started_at", "started_at"),
        Index("ix_device_assignments_ended_at", "ended_at"),
        Index(
            "ux_device_assignments_active_device",
            "device_id",
            unique=True,
            postgresql_where=text("ended_at IS NULL"),
            sqlite_where=text("ended_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=False,
    )
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("athletes.id"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    device = relationship("Device", back_populates="assignments")
    athlete = relationship("Athlete", back_populates="assignments")
