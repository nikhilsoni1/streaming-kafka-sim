from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.database_access.sessions.log_registry_session_local import LogRegistrySessionLocal
from render_rig2.database_access.models.log_registry_model import LogsDlReg
from time import perf_counter
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse
from typing import Tuple

def parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """
    Extracts the bucket and key from an S3 URI.

    Args:
        s3_uri (str): e.g., "s3://bucket-name/path/to/file.ext"

    Returns:
        Tuple[str, str]: (bucket_name, key)
    """
    if not s3_uri.startswith("s3://"):
        logger.error("Invalid S3 URI. Must start with 's3://'.")
        raise ValueError("Invalid S3 URI. Must start with 's3://'.")
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key

@celery_app.task(name="lookup_log_registry")
def lookup_log_registry(log_id: str) -> Tuple[str, str, str] | None:
    """
    Looks up the LogsDlReg entry for a given log_id.
    Returns:
        - log_id: The log ID.
        - bucket_name: The S3 bucket name.
        - key: The S3 object key.
    """
    db = LogRegistrySessionLocal()
    try:
        t0 = perf_counter()
        result = (
            db.query(
                LogsDlReg.file_s3_path,
            )
            .filter_by(log_id=log_id)
            .first()
        )
        t1 = perf_counter()
        el1 = t1 - t0
        logger.info(
            f"lookup_log_registry took {el1:.4f} seconds for log_id: {log_id}"
        )
        if result:
            bucket_name, key = parse_s3_uri(result.file_s3_path)
            return log_id, bucket_name, key
        return None
    except SQLAlchemyError as e:
        logger.exception(f"Database error while querying LogsDlReg: {e}")
        raise RuntimeError(f"Database error while querying LogsDlReg: {e}")
