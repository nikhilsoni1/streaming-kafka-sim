# parser_adapter.py
from ypr_core_logfoundry.parser import ULogParser
import os
from render_rig.data_access import get_file3path_from_logregistry
from render_rig.data_access import s3_get_object_by_uri

def get_log_data(log_id: str) -> dict:
    """
    Fetch and parse ULog data for a given log_id.

    Args:
        log_id (str): Identifier for the ULog file.

    Returns:
        dict: Parsed ULog data where each topic maps to a Pandas DataFrame.
    """

    if log_id is None:
        raise ValueError("log_id cannot be None")

    s3_uri = get_file3path_from_logregistry(log_id)
    ulog_path = s3_get_object_by_uri(s3_uri=s3_uri, region_name="us-east-1", mode="cache")

    if not os.path.exists(ulog_path):
        raise FileNotFoundError(f"ULog file not found at {ulog_path}")

    parsed_log = ULogParser(ulog_path)

    # You could normalize keys or filter unwanted topics here if needed
    return parsed_log

if __name__ == "__main__":
    # Example usage
    log_id = "a224339a-2537-480d-990e-1e30197ee72e"
    log_data = get_log_data(log_id)
    print(log_data)
    debug = True
