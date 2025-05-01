# manager.py
import time
from collections import OrderedDict
from pprint import pprint
# import charts
from render_rig.chart_engine.charts.chart_acceleration_raw_xyz import ChartAccelRawXYZ

# import parser
from render_rig.logfoundry_bridge.parser_adapter import get_log_data

# import utils
from render_rig.utils.time_utils import get_utc_now
from render_rig.utils.hash_utils import hash_bytes_sha256

# import object access
from render_rig.data_access.object_access.session_manager import create_boto3_client
from render_rig.data_access.object_access import s3_save_chart_json
from render_rig.data_access.object_access import s3_get_chart_json

# import database access
from render_rig.data_access.database.session_manager import get_log_registry_session
from render_rig.data_access.database.session_manager import get_render_rig_session
from render_rig.data_access.database.repository.render_rig_registry import insert_into_chart_registry
from render_rig.data_access.database.repository.render_rig_registry import lookup_chart_registry

# import standard libraries
import os
from uuid import uuid4

from render_rig.utils.logger import setup_logger

# This will log to both console (stdout) and file
logger = setup_logger("logs/render_rig.log")


def generate_charts_for_log(log_id: str) -> list:
    time_dict = OrderedDict()
    a = time.monotonic()
    bucket_name = os.getenv("RENDER_RIG_CHARTS_BUCKET_NAME", None)
    if bucket_name is None:
        raise ValueError("BUCKET_NAME environment variable is not set.")
    b = time.monotonic()
    time_dict["bucket_name"] = b - a

    a = time.monotonic()
    ALL_CHARTS = [ChartAccelRawXYZ()]
    b = time.monotonic()
    time_dict["chart_list"] = b - a

    a = time.monotonic()
    db_render_rig_session = get_render_rig_session()
    b = time.monotonic()
    time_dict["db_render_rig_session"] = b - a

    a = time.monotonic()
    db_log_registry_session = get_log_registry_session()
    b = time.monotonic()
    time_dict["db_log_registry_session"] = b - a

    a = time.monotonic()
    s3_client = create_boto3_client("s3", region_name="us-east-1", max_retries=3)
    b = time.monotonic()
    time_dict["s3_client"] = b - a
    
    a = time.monotonic()
    log_data = get_log_data(log_id, db_log_registry_session, s3_client)
    b = time.monotonic()
    time_dict["log_data"] = b - a
    results = []

    chart_times = list()
    for chart in ALL_CHARTS:
        _d = OrderedDict()

        a = time.monotonic()
        lookup_result = lookup_chart_registry(log_id, chart.chart_name, session=db_render_rig_session)
        b = time.monotonic()
        _d["lookup_chart_registry"] = b - a

        if lookup_result is not None:
            a = time.monotonic()
            bucket_name, key = lookup_result
            chart_json = s3_get_chart_json(
                bucket_name=bucket_name,
                key=key,
                s3_client=s3_client)
            b = time.monotonic()
            _d["s3_get_chart_json"] = b - a
            chart_times.append({chart.chart_name: _d})
            continue

        if chart.is_topic_available(log_data):
            a = time.monotonic()
            fig = chart.generate(log_data)
            b = time.monotonic()
            _d["generate_chart"] = b - a

            a = time.monotonic()
            chat_json = fig.to_json()
            chat_json_encoded = chat_json.encode("utf-8")
            b = time.monotonic()
            _d["to_json"] = b - a

            a = time.monotonic()
            log_ts_utc = get_utc_now()
            upd_ts_utc = log_ts_utc
            _log_id = log_id
            chart_id = str(uuid4().hex)
            chart_name = chart.chart_name
            chart_hash_sha256 = hash_bytes_sha256(chat_json_encoded)
            key = f"charts/{_log_id}/{chart_name}/{chart_id}.json"
            b = time.monotonic()
            _d["chart_metadata"] = b - a

            a = time.monotonic()
            s3_save_success = s3_save_chart_json(
                chart_json_str=chat_json_encoded,
                bucket_name=bucket_name,
                key=key,
                s3_client=s3_client
            )
            b = time.monotonic()
            _d["s3_save_chart_json"] = b - a
            if not s3_save_success:
                raise ValueError("Failed to save chart JSON to S3.")
            
            a = time.monotonic()
            insert_success = insert_into_chart_registry(
                log_ts_utc=log_ts_utc,
                upd_ts_utc=upd_ts_utc,
                log_id=_log_id,
                chart_id=chart_id,
                chart_name=chart_name,
                chart_hash_sha256=chart_hash_sha256,
                bucket_name=bucket_name,
                key=key,
                session=db_render_rig_session
            )
            b = time.monotonic()
            _d["insert_into_chart_registry"] = b - a
            if insert_success is None:
                raise ValueError("Failed to insert chart metadata into registry.")
            # results.append({"chart_id": chart_id, "status": "generated"})
        chart_times.append({chart.chart_name: _d})
    time_dict["chart_times"] = chart_times
    return time_dict

if __name__ == "__main__":
    import json
    # Example usage
    log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
    a = time.monotonic()
    results = generate_charts_for_log(log_id)
    b = time.monotonic()
    print(f"Time taken to generate charts: {b - a} seconds")
    with open("chart_times.json", "w") as f:
        json.dump(results, f, indent=4)
