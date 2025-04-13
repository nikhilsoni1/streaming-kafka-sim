from typing import Optional

from sqlalchemy import Date, DateTime, Double, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(DeclarativeBase):
    pass


class RawDbinfo(Base):
    __tablename__ = 'raw_dbinfo'
    __table_args__ = (
        PrimaryKeyConstraint('row_id', name='raw_dbinfo_pkey'),
        {'schema': 'dbinfo'}
    )

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[datetime.datetime] = mapped_column(DateTime)
    log_ts_utc: Mapped[datetime.datetime] = mapped_column(DateTime)
    type: Mapped[Optional[str]] = mapped_column(Text)
    log_id: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(Text)
    sys_hw: Mapped[Optional[str]] = mapped_column(Text)
    ver_sw: Mapped[Optional[str]] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    log_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    mav_type: Mapped[Optional[str]] = mapped_column(Text)
    estimator: Mapped[Optional[str]] = mapped_column(Text)
    video_url: Mapped[Optional[str]] = mapped_column(Text)
    duration_s: Mapped[Optional[float]] = mapped_column(Double(53))
    wind_speed: Mapped[Optional[float]] = mapped_column(Double(53))
    description: Mapped[Optional[str]] = mapped_column(Text)
    error_labels: Mapped[Optional[dict]] = mapped_column(JSONB)
    flight_modes: Mapped[Optional[dict]] = mapped_column(JSONB)
    vehicle_name: Mapped[Optional[str]] = mapped_column(Text)
    vehicle_uuid: Mapped[Optional[str]] = mapped_column(Text)
    airframe_name: Mapped[Optional[str]] = mapped_column(Text)
    airframe_type: Mapped[Optional[str]] = mapped_column(Text)
    ver_sw_release: Mapped[Optional[str]] = mapped_column(Text)
    sys_autostart_id: Mapped[Optional[str]] = mapped_column(Text)
    num_logged_errors: Mapped[Optional[int]] = mapped_column(Integer)
    num_logged_warnings: Mapped[Optional[int]] = mapped_column(Integer)
    flight_mode_durations: Mapped[Optional[dict]] = mapped_column(JSONB)
