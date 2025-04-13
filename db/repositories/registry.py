from sqlalchemy.orm import Session
from db.models.registry import LogsDlReg
import datetime
from typing import Optional
from typing import List
from typing import Dict
from pytz import UTC
from sqlalchemy import text
from sqlalchemy import insert
from sqlalchemy import update
import uuid
from sqlalchemy.exc import SQLAlchemyError
import traceback
from tqdm import tqdm
import datetime
import json


def get_utc_now(str=False):
    utc_now = datetime.datetime.now(UTC).replace(tzinfo=None)
    if str:
        return utc_now.strftime("%Y-%m-%d %H:%M:%S")
    return utc_now


class LogDlRepository:
    def __init__(self, session: Session, batch_size: int = 5000):
        self.session = session
        self.batch_size = batch_size

    def insert_logs_in_process(self, log_ids: List[str], job_id, log_ts_utc):
        """
        Insert records into LogsDlReg with just log_id and status='in_process'.
        On failure, write each failed batch to a JSON file in the current working directory.
        """
        insert_stmt = insert(LogsDlReg)

        def chunked(data, size):
            for i in range(0, len(data), size):
                yield data[i: i + size]

        # Compose full rows from log_ids
        enriched_logs = [
            {
                "log_id": log_id,
                "status": "in_process",
                "log_ts_utc": log_ts_utc,
                "job_id": job_id,
            }
            for log_id in log_ids
        ]

        chunks = chunked(enriched_logs, self.batch_size)
        chunks = tqdm(chunks, desc="Inserting log records", unit="batch")

        for i, chunk in enumerate(chunks):
            try:
                self.session.execute(insert_stmt, chunk)
                self.session.commit()
            except SQLAlchemyError as e:
                self.session.rollback()

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
                        EXTRACT(YEAR FROM t1.log_date)::int AS log_year,
                        EXTRACT(MONTH FROM t1.log_date)::int AS log_month,
                        EXTRACT(DAY FROM t1.log_date)::int AS log_day
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

    def update_logs_by_job_and_log_id(self, updates: List[Dict]):
        """
        Chunked batch update of LogsDlReg records using job_id and log_id.

        Parameters:
            updates (List[Dict]): Each dict must include:
                - job_id
                - log_id
                - Optional: status, upd_ts_utc, file_* fields, stdout, stderr
        """
        failed_batches = []

        def chunked(data, size):
            for i in range(0, len(data), size):
                yield data[i:i + size]

        chunks = chunked(updates, self.batch_size)
        chunks = tqdm(chunks, desc="Updating logs", unit="batch")

        for i, chunk in enumerate(chunks):
            try:
                for record in chunk:
                    update_fields = {
                        k: v for k, v in record.items()
                        if k not in {"job_id", "log_id"} and v is not None
                    }

                    if not update_fields:
                        continue  # nothing to update

                    stmt = (
                        update(LogsDlReg)
                        .where(
                            LogsDlReg.job_id == record["job_id"],
                            LogsDlReg.log_id == record["log_id"]
                        )
                        .values(**update_fields)
                    )

                    self.session.execute(stmt)

                self.session.commit()

            except SQLAlchemyError as e:
                self.session.rollback()
                failed_batches.append({
                    "batch_index": i,
                    "records": chunk,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        if failed_batches:
            print(f"{len(failed_batches)} batch(es) failed during update.")
            for fail in failed_batches:
                print(fail)