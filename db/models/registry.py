from typing import Optional

from sqlalchemy import DateTime, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(DeclarativeBase):
    pass


class LogsDlReg(Base):
    __tablename__ = 'logs_dl_reg'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='logs_dl_reg_pkey'),
        {'schema': 'registry'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    log_ts_utc: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    upd_ts_utc: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    log_id: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Text)
    file_s3_path: Mapped[Optional[str]] = mapped_column(Text)
    file_sha256: Mapped[Optional[str]] = mapped_column(Text)
    file_name: Mapped[Optional[str]] = mapped_column(Text)
    file_ext: Mapped[Optional[str]] = mapped_column(Text)
    stdout: Mapped[Optional[str]] = mapped_column(Text)
    stderr: Mapped[Optional[str]] = mapped_column(Text)
