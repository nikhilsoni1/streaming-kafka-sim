from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models.registry import LogsDlReg
from db.models.transformed_data import t_clean_dbinfo
import datetime
from typing import Optional
from pytz import UTC
from sqlalchemy import select
from sqlalchemy.orm import aliased

def get_utc_now(str=False):
    utc_now = datetime.datetime.now(UTC).replace(tzinfo=None)
    if str:
        return utc_now.strftime('%Y-%m-%d %H:%M:%S')
    return utc_now

class LogDlRepository:
    def __init__(self, session: Session):
        self.session = session

    def mark_log_id_as_in_process(self, log_id_list: list[str]) -> Optional[list[str]]:
        try:
            new_logs = list()
            for log_id in log_id_list:
                _now = get_utc_now(str=True)
                new_log = LogsDlReg(
                    log_id=log_id,
                    status='in_process',
                    log_ts_utc=_now,
                    upd_ts_utc=_now,
                )
                new_logs.append(new_log)
            self.session.bulk_save_objects(new_logs)
            self.session.commit()
            return log_id_list
        except IntegrityError:
            self.session.rollback()
            return None

    def get_new_log_ids(self) -> list[str]:
        ldr = aliased(LogsDlReg)
        subq = (
            select(ldr.log_id)
            .where(ldr.status.in_(['in_process', 'succeeded', 'failed']))
        )
        stmt = (
            select(t_clean_dbinfo.c.log_id)
            .where(t_clean_dbinfo.c.log_id.not_in(subq))
            .order_by(t_clean_dbinfo.c.updated_at_utc.desc())
            .limit(10)
        )
        result = self.session.execute(stmt).scalars().all()
        return result

    def update_log_id_records(self, upd: list[dict]) -> Optional[list[dict]]:
        try:
            for item in upd:
                try:
                    self.session.merge(LogsDlReg(**item))
                except Exception as e:
                    print(f"Failed to merge record with log_id {item.get('log_id')}: {e}")
            self.session.commit()
            return upd
        except Exception as e:
            self.session.rollback()
            print(f"Failed to update log records: {e}")
            return None