from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import RawDbinfo
import datetime
from typing import Optional
from pytz import timezone, UTC


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
    
    def get_by_hash(self, hash_sha256: str) -> Optional[RawDbinfo]:
        return self.db.query(RawDbinfo).filter(RawDbinfo.hash_sha256 == hash_sha256).first()

    def delete_by_hash(self, hash_sha256: str) -> bool:
        try:
            entry = self.db.query(RawDbinfo).filter(RawDbinfo.hash_sha256 == hash_sha256).first()
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error during deletion: {e}")
            return False

    def get_all(self, limit: Optional[int] = None) -> list[RawDbinfo]:
        query = self.db.query(RawDbinfo)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def update_raw_json(self, hash_sha256: str, new_raw_json: dict, new_raw_json_b64: str) -> Optional[RawDbinfo]:
        try:
            entry = self.db.query(RawDbinfo).filter(RawDbinfo.hash_sha256 == hash_sha256).first()
            if entry:
                entry.raw_json = new_raw_json
                entry.raw_json_b64 = new_raw_json_b64
                self.db.commit()
                self.db.refresh(entry)
                return entry
            return None
        except Exception as e:
            self.db.rollback()
            print(f"Error during update: {e}")
            return None

    def list_all_dbinfo_versions(self, limit: Optional[int] = None) -> list[tuple[datetime.datetime, str]]:
        query = (
            self.db.query(RawDbinfo.log_ts_utc, RawDbinfo.hash_sha256)
            .order_by(RawDbinfo.log_ts_utc.desc())
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()
