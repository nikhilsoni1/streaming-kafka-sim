import json
import traceback
from datetime import datetime, timezone
from typing import List
import os

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import insert
from tqdm import tqdm

from db.models import RawDbinfo  # Adjust path as needed


class RawDbinfoRepository:
    def __init__(
        self, session: Session, failure_log_dir: str = ".", batch_size: int = 5000
    ):
        self.session = session
        self.failure_log_dir = failure_log_dir
        self.batch_size = batch_size

    def write_records(self, records: List[dict], use_tqdm: bool = False):
        """
        Fast insert using SQLAlchemy Core insert + executemany.
        Records are batched, and failed batches are saved to a local JSON file.
        """
        failed_batches = []
        insert_stmt = insert(RawDbinfo)

        def chunked(data, size):
            for i in range(0, len(data), size):
                yield data[i : i + size]

        chunks = chunked(records, self.batch_size)
        chunks = (
            tqdm(chunks, desc="Inserting batches", unit="batch") if use_tqdm else chunks
        )

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
            print(f"[WARNING] {len(failed_batches)} batch(es) failed to insert.")
            self._write_failures_to_file(failed_batches)

    def _write_failures_to_file(self, failed_batches: List[dict]):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"failed_raw_dbinfo_batches_{timestamp}.json"
        filepath = os.path.join(self.failure_log_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(failed_batches, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Wrote failed batch records to {filepath}")
        except Exception as e:
            print("[ERROR] Failed to write failed records to file:", e)
