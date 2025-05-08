from sqlalchemy import DateTime, PrimaryKeyConstraint, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime


class Base(DeclarativeBase):
    pass


class ChartRegistry(Base):
    __tablename__ = "chart_registry"
    __table_args__ = (
        PrimaryKeyConstraint("log_id", "chart_name", name="chart_registry_pkey"),
        {"schema": "registry"},
    )

    log_ts_utc: Mapped[datetime.datetime] = mapped_column(DateTime)
    upd_ts_utc: Mapped[datetime.datetime] = mapped_column(DateTime)
    log_id: Mapped[str] = mapped_column(Text, primary_key=True)
    chart_id: Mapped[str] = mapped_column(Text)
    chart_name: Mapped[str] = mapped_column(Text, primary_key=True)
    chart_hash_sha256: Mapped[str] = mapped_column(Text)
    bucket_name: Mapped[str] = mapped_column(Text)
    key: Mapped[str] = mapped_column(Text)
