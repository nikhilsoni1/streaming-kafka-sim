# parser_adapter.py
from ypr_core_logfoundry.parser import ULogParser
import os

# Assume that ULog files are saved under 'render_rig/ulogs/{log_id}.ulg'
ULOG_DIRECTORY = os.getenv("ULOG_DIRECTORY", "render_rig/ulogs")

def get_log_data(log_id: str) -> dict:
    """
    Fetch and parse ULog data for a given log_id.

    Args:
        log_id (str): Identifier for the ULog file.

    Returns:
        dict: Parsed ULog data where each topic maps to a Pandas DataFrame.
    """
    ulog_path = os.path.join(ULOG_DIRECTORY, f"{log_id}.ulg")

    if not os.path.exists(ulog_path):
        raise FileNotFoundError(f"ULog file not found at {ulog_path}")

    parsed_log = ULogParser(ulog_path)

    # You could normalize keys or filter unwanted topics here if needed
    return parsed_log
