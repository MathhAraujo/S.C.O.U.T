import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TemperatureMeasurement(Base):
    __tablename__ = "temperature_measurements"
    __table_args__ = (
        Index("ix_temperature_measurements_device_id", "device_id"),
        Index("ix_temperature_measurements_athlete_id", "athlete_id"),
        Index("ix_temperature_measurements_received_at", "received_at"),
        Index("ix_temperature_measurements_device_received_at", "device_id", "received_at"),
        Index("ix_temperature_measurements_athlete_received_at", "athlete_id", "received_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=False,
    )
    athlete_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("athletes.id"),
        nullable=True,
    )
    sensor: Mapped[str] = mapped_column(String(50), nullable=False)
    value_celsius: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="celsius", nullable=False)
    uptime_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    measured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    device = relationship("Device", back_populates="temperature_measurements")
    athlete = relationship("Athlete", back_populates="temperature_measurements")
