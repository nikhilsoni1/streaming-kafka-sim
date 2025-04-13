import json
import traceback
from datetime import datetime
from typing import List
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from db.models import RawDbinfo  # adjust this path if needed
from tqdm import tqdm


class RawDbinfoRepository:
    def __init__(self, session: Session, failure_log_dir: str = "."):
        self.session = session
        self.failure_log_dir = failure_log_dir

    def write_records(self, records: List[dict], use_tqdm: bool = False):
        failed = []

        iterable = tqdm(records, desc="Inserting records", unit="record") if use_tqdm else records

        for i, record_dict in enumerate(iterable):
            try:
                record = RawDbinfo(**record_dict)
                self.session.add(record)
                self.session.flush()
            except SQLAlchemyError as e:
                self.session.rollback()
                failed.append({
                    "index": i,
                    "record": record_dict,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        try:
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            print("[CRITICAL] Commit failed after flushing valid records:", e)
            return

        if failed:
            print(f"[WARNING] {len(failed)} record(s) failed to insert.")
            self._write_failures_to_file(failed)

    def _write_failures_to_file(self, failed_rows: List[dict]):
        timestamp = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H-%M-%S")
        filename = f"failed_raw_dbinfo_{timestamp}.json"
        filepath = os.path.join(self.failure_log_dir, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(failed_rows, f, indent=2)
            print(f"[INFO] Wrote failed records to {filepath}")
        except Exception as e:
            print("[ERROR] Failed to write failed records to file:", e)
