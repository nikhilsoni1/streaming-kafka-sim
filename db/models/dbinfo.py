from sqlalchemy import DateTime, Integer, PrimaryKeyConstraint, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(DeclarativeBase):
    pass


class RawDbinfo(Base):
    __tablename__ = 'raw_dbinfo'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='raw_dbinfo_pkey'),
        UniqueConstraint('hash_sha256', name='raw_dbinfo_hash_sha256_key'),
        {'schema': 'dbinfo'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    log_ts_utc: Mapped[datetime.datetime] = mapped_column(DateTime)
    hash_sha256: Mapped[str] = mapped_column(Text)
    raw_json: Mapped[dict] = mapped_column(JSONB)
    raw_json_b64: Mapped[str] = mapped_column(Text)
