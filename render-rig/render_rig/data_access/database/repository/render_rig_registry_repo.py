import os
from typing import Optional
from ypr_data_connector.database_client import PostgresDatabaseClient
from render_rig.data_access.database.models import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import psycopg2.errors


def get_render_rig_session() -> Session:
    """
    Creates and returns a SQLAlchemy session connected to the RenderRig Postgres database.

    Environment Variables Required:
        - DATABASE_USER: Username for the database.
        - DATABASE_PASSWORD: Password for the database.
        - DATABASE_HOST: Hostname or IP address of the database.
        - DATABASE_PORT: Port number of the database.
        - DATABASE_NAME: Name of the database.

    Returns:
        Session: A SQLAlchemy database session for executing queries.

    Raises:
        EnvironmentError: If any required environment variable is missing.
        ConnectionError: If the connection test fails.
        RuntimeError: For any other unexpected errors during session creation.
    """
    try:
        database_user = os.environ["DATABASE_USER"]
        database_password = os.environ["DATABASE_PASSWORD"]
        database_host = os.environ["DATABASE_HOST"]
        database_port = os.environ["DATABASE_PORT"]
        database_name = os.environ.get("DATABASE_NAME")

        postgres_client = PostgresDatabaseClient(
            database_host=database_host,
            database_port=database_port,
            database_user=database_user,
            database_password=database_password,
            database_name=database_name,
        )

        if postgres_client.test_connection():
            print("Postgres connection successful")
            return postgres_client.get_session()
        else:
            raise ConnectionError("Postgres connection failed during test.")
    except KeyError as e:
        raise EnvironmentError(f"Missing required environment variable: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Postgres session: {e}")

def insert_into_chart_registry(
    log_ts_utc: str,
    upd_ts_utc: str,
    log_id: str,
    chart_id: str,
    chart_name: str,
    chart_hash_sha256: str,
    bucket_name: str,
    key: str,
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

        session = get_render_rig_session()
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


if __name__ == "__main__":
    # Example usage
    import datetime
    _now = datetime.datetime.now(datetime.timezone.utc)
    _now = _now.strftime("%Y-%m-%d %H:%M:%S")
    log_ts_utc = _now
    upd_ts_utc = _now
    log_id = "example_log_id"
    chart_id = "example_chart_id"
    chart_name = "example_chart_name"
    chart_hash_sha256 = "example_hash"
    bucket_name = "example_bucket"
    key = "example_key"

    insert_into_chart_registry(
        log_ts_utc,
        upd_ts_utc,
        log_id,
        chart_id,
        chart_name,
        chart_hash_sha256,
        bucket_name,
        key,
    )
