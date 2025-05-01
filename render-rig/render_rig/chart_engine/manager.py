# manager.py
import time
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

a = time.monotonic()
ALL_CHARTS = [ChartAccelRawXYZ()]
db_render_rig_session = get_render_rig_session()
db_log_registry_session = get_log_registry_session()
s3_client = create_boto3_client("s3", region_name="us-east-1", max_retries=3)
b = time.monotonic()
print(f"Time taken to create sessions and S3 client: {b - a} seconds")

def generate_charts_for_log(log_id: str) -> list:
    log_data = get_log_data(log_id, db_log_registry_session, s3_client)
    results = []

    for chart in ALL_CHARTS:
        chart_id = f"{log_id}_{chart.chart_name}"
        lookup_result = lookup_chart_registry(log_id, chart.chart_name, session=db_render_rig_session)
        if lookup_result is not None:
            bucket_name, key = lookup_result
            chart_json = s3_get_chart_json(
                bucket_name=bucket_name,
                key=key,
                s3_client=s3_client)
            pld = dict()
            pld["chart_json"] = chart_json
            pld["chart_id"] = log_id
            pld["status"] = "cache"
            results.append(pld)
            print(f"Chart {chart.chart_name} already exists in the registry.")
            continue

        if chart.is_topic_available(log_data):
            fig = chart.generate(log_data)
            fig_json = fig.to_json()
            fig_json_encoded = fig_json.encode("utf-8")
            log_ts_utc = get_utc_now()
            upd_ts_utc = log_ts_utc
            _log_id = log_id
            chart_id = str(uuid4().hex)
            chart_name = chart.chart_name
            chart_hash_sha256 = hash_bytes_sha256(fig_json_encoded)
            bucket_name = os.getenv("RENDER_RIG_CHARTS_BUCKET_NAME", None)
            if bucket_name is None:
                raise ValueError("BUCKET_NAME environment variable is not set.")
            key = f"charts/{_log_id}/{chart_name}/{chart_id}.json"
            s3_save_success = s3_save_chart_json(
                chart_json_str=fig_json,
                bucket_name=bucket_name,
                key=key,
                s3_client=s3_client
            )
            if s3_save_success:
                pass
            else:
                raise ValueError("Failed to save chart JSON to S3.")
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
            if insert_success is not None:
                pass
            else:
                raise ValueError("Failed to insert chart metadata into registry.")
            results.append({"chart_id": chart_id, "status": "generated"})
        else:
            # log
            pass

    return results

if __name__ == "__main__":
    # Example usage
    log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
    a = time.monotonic()
    results = generate_charts_for_log(log_id)
    b = time.monotonic()
    print(f"Time taken to generate charts: {b - a} seconds")
    for result in results:
        print(f"Chart ID: {result['chart_id']}, Status: {result['status']}")
