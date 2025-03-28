from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import RawDbinfo
import datetime
from typing import Optional


class RawDbinfoRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        log_ts_utc: datetime.datetime,
        hash_sha256: str,
        raw_json: dict,
        raw_json_b64: str
    ) -> Optional[RawDbinfo]:
        try:
            entry = RawDbinfo(
                log_ts_utc=log_ts_utc,
                hash_sha256=hash_sha256,
                raw_json=raw_json,
                raw_json_b64=raw_json_b64,
            )
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            return entry
        except IntegrityError:
            self.db.rollback()
            print("Duplicate encountered, skipping.")
            return None
