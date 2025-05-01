# parser_adapter.py
from ypr_core_logfoundry.parser import ULogParser
import os
from render_rig.data_access.database.repository.px4_registry import get_s3uri_from_logregistry
from render_rig.data_access.object_access.s3 import s3_get_object_by_uri
from render_rig.data_access.object_access.s3 import StorageMode
from boto3 import client
from sqlalchemy.orm import Session


def get_log_data(
    log_id: str,
    db_session: Session,
    s3_client: client = None,
    mode: StorageMode = "cache",
    cache_dir: str = "/tmp/s3_cache",
) -> dict:
    """
    Fetch and parse ULog data for a given log_id.

    Args:
        log_id (str): Identifier for the ULog file.

    Returns:
        dict: Parsed ULog data where each topic maps to a Pandas DataFrame.
    """

    if log_id is None:
        raise ValueError("log_id cannot be None")

    s3_uri = get_s3uri_from_logregistry(log_id, db_session)
    ulog_path = s3_get_object_by_uri(
        s3_uri=s3_uri,
        s3_client=s3_client,
        mode=mode,
        cache_dir=cache_dir,
    )

    if not os.path.exists(ulog_path):
        raise FileNotFoundError(f"ULog file not found at {ulog_path}")

    parsed_log = ULogParser(ulog_path)

    # You could normalize keys or filter unwanted topics here if needed
    return parsed_log


if __name__ == "__main__":
    pass
