from typing import Optional
from typing import Tuple
from render_rig.data_access.database.models.render_rig_registry_model import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import psycopg2.errors

def insert_into_chart_registry(
    log_ts_utc: str,
    upd_ts_utc: str,
    log_id: str,
    chart_id: str,
    chart_name: str,
    chart_hash_sha256: str,
    bucket_name: str,
    key: str,
    session: Session
) -> Optional[str]:
    """
    Inserts a new chart metadata record into the ChartRegistry table.
    If the record already exists (based on unique constraint), skips insertion gracefully.

    Returns:
        Optional[str]: The chart ID if insertion is successful; None if record already exists.
    """
    session: Optional[Session] = None
    try:
        record = ChartRegistry(
            log_ts_utc=log_ts_utc,
            upd_ts_utc=upd_ts_utc,
            log_id=log_id,
            chart_id=chart_id,
            chart_name=chart_name,
            chart_hash_sha256=chart_hash_sha256,
            bucket_name=bucket_name,
            key=key,
        )
        session.add(record)
        session.commit()
        print(f"Inserted chart {chart_id} successfully.")
        return chart_id

    except IntegrityError as e:
        if isinstance(e.orig, psycopg2.errors.UniqueViolation):
            print(f"Record for (log_id={log_id}, chart_name={chart_name}) already exists. Skipping insert.")
            if session:
                session.rollback()
            return None
        else:
            if session:
                session.rollback()
            raise RuntimeError(f"Integrity error during chart insert: {e}")

    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise RuntimeError(f"Database error while inserting chart: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error during insertion: {e}")

    finally:
        if session:
            try:
                session.close()
            except Exception as e:
                print(f"Warning: Error closing session: {e}")

def lookup_chart_registry(log_id: str, chart_name: str, session: Session) -> Optional[Tuple[str, str]]:
    """
    Looks up the ChartRegistry entry for a given log_id and chart_name.

    Returns:
        Optional[Tuple[str, str]]: (bucket_name, key) if the record exists, else None.
    """
    try:
        result = session.query(ChartRegistry).filter_by(log_id=log_id, chart_name=chart_name).first()
        if result:
            return result.bucket_name, result.key
        return None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Database error while querying ChartRegistry: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    pass
