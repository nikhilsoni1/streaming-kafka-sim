from sqlalchemy.orm import Session
from db.models.registry import LogsDlReg
import datetime
from typing import Optional
from typing import List
from typing import Dict
from pytz import UTC
from sqlalchemy import text
from sqlalchemy import insert
import uuid
from sqlalchemy.exc import SQLAlchemyError
import traceback
from tqdm import tqdm
import datetime


def get_utc_now(str=False):
    utc_now = datetime.datetime.now(UTC).replace(tzinfo=None)
    if str:
        return utc_now.strftime("%Y-%m-%d %H:%M:%S")
    return utc_now


class LogDlRepository:
    def __init__(self, session: Session, batch_size: int = 5000):
        self.session = session
        self.batch_size = batch_size

    def insert_logs_in_process(self, logs: List[Dict]):
        """
        Insert records into LogsDlReg with status='in_process'.
        """
        failed_batches = []
        insert_stmt = insert(LogsDlReg)

        def chunked(data, size):
            for i in range(0, len(data), size):
                yield data[i : i + size]

        # Add 'status': 'in_process' to each record
        enriched_logs = [
            {
                **log,
                "status": "in_process",
                "log_ts_utc": datetime.datetime.now(datetime.UTC).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            for log in logs
        ]

        chunks = chunked(enriched_logs, self.batch_size)
        chunks = tqdm(chunks, desc="Inserting log records", unit="batch")

        for i, chunk in enumerate(chunks):
            try:
                self.session.execute(insert_stmt, chunk)
                self.session.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                failed_batches.append(
                    {
                        "batch_index": i,
                        "records": chunk,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )

        if failed_batches:
            print(f"{len(failed_batches)} batch(es) failed during insert.")

    def get_new_log_entries(self, limit: int = 10) -> List[dict]:
        # Generate job_id once for all rows
        job_id = str(uuid.uuid4())

        # Raw SQL query
        query = f"""
                    WITH job_cte AS (
                        SELECT gen_random_uuid()::text AS job_id
                    )
                    SELECT 
                        t1.log_id,
                        t1.log_date,
                        EXTRACT(YEAR FROM t1.log_date)::int AS log_year,
                        EXTRACT(MONTH FROM t1.log_date)::int AS log_month,
                        EXTRACT(DAY FROM t1.log_date)::int AS log_day,
                        gen_random_uuid()::text AS task_id,
                        job_cte.job_id
                    FROM transformed_data.dbinfo_sample_1k t1,
                        job_cte
                    WHERE t1.log_id NOT IN (
                        SELECT log_id
                        FROM registry.logs_dl_reg
                        WHERE status IN ('in_process', 'succeeded', 'failed')
                    )
                    LIMIT {limit};
                """
        query = text(query)
        # Execute query with params
        result = self.session.execute(query).mappings().all()
        # Convert RowMapping to list of dicts
        return [dict(row) for row in result]

    def update_log_id_records(self, upd: list[dict]) -> Optional[list[dict]]:
        try:
            for item in upd:
                try:
                    self.session.merge(LogsDlReg(**item))
                except Exception as e:
                    print(
                        f"Failed to merge record with log_id {item.get('log_id')}: {e}"
                    )
            self.session.commit()
            return upd
        except Exception as e:
            self.session.rollback()
            print(f"Failed to update log records: {e}")
            return None
