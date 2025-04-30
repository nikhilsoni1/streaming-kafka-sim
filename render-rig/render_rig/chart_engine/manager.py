# manager.py

from render_rig.chart_engine.charts.chart_acceleration_raw_xyz import ChartAccelRawXYZ
from render_rig.logfoundry_bridge.parser_adapter import get_log_data
from render_rig.cache.store import save_chart_json
from render_rig.cache.store import chart_exists
from render_rig.utils.time_utils import get_utc_now
from uuid import uuid4
from render_rig.utils.hash_utils import hash_bytes_sha256
from render_rig.data_access.object_access import s3_save_chart_json
from render_rig.data_access.object_access import s3_get_chart_json
from render_rig.data_access.database import insert_into_chart_registry
from render_rig.data_access.database import lookup_chart_registry
import os

ALL_CHARTS = [ChartAccelRawXYZ()]


def generate_charts_for_log(log_id: str) -> list:
    log_data = get_log_data(log_id)
    results = []

    for chart in ALL_CHARTS:
        chart_id = f"{log_id}_{chart.chart_name}"
        lookup_result = lookup_chart_registry(log_id, chart.chart_name)
        if lookup_result is not None:
            bucket_name, key = lookup_result
            chart_json = s3_get_chart_json(
                bucket_name=bucket_name,
                key=key,
                region_name="us-east-1")
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
            bucket_name = os.getenv("CHARTS_BUCKET_NAME", None)
            if bucket_name is None:
                raise ValueError("BUCKET_NAME environment variable is not set.")
            key = f"charts/{_log_id}/{chart_name}/{chart_id}.json"
            s3_save_success = s3_save_chart_json(
                chart_json_str=fig_json,
                bucket_name=bucket_name,
                key=key,
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
    results = generate_charts_for_log(log_id)
    for result in results:
        print(f"Chart ID: {result['chart_id']}, Status: {result['status']}")
