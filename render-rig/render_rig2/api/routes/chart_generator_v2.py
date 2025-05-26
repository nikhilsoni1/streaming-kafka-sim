import os
import uuid
from fastapi import APIRouter
from fastapi import Request
from redis import Redis
from celery import chain
from render_rig2.utils.logger import logger
from render_rig2.chart_engine import CHART_REGISTRY
from render_rig2.tasks import lookup_log_registry
from render_rig2.tasks import lookup_chart_registry
from render_rig2.tasks import get_existing_chart
from render_rig2.tasks import get_log_dispatch_chart
from render_rig2.tasks import log_chart_in_registry
from render_rig2.tasks import store_chart_json_in_s3

redis_client = Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB_STATUS"))
)

router = APIRouter()

@router.post("/{log_id}/{chart_name}")
async def generate_chart_v2(log_id: str, chart_name: str, request: Request):
    """
    NEW async-first chart generation endpoint.
    Will support:
    - 202 Accepted
    - Redis task status tracking
    - optional webhook delivery
    """
    task_id = str(uuid.uuid4().hex)
    redis_client.set(f"task_status:{task_id}", "queued")
    # return {
    #     "message": "This is the new v2 chart generator route.",
    #     "log_id": log_id,
    #     "chart_name": chart_name
    # }
    logger.debug(f"Generating chart for log_id: {log_id}, chart_name: {chart_name}")
    chart_data = None
    pipeline1 = chain(
        lookup_chart_registry.s(log_id, chart_name),
        get_existing_chart.s(),
    )
    try:
        result1 = pipeline1.apply_async()
        chart_data = result1.get(timeout=60)
    except Exception as e:
        logger.error(f"Error in pipeline1: {e}")
        chart_data = None


    if chart_data is not None:
        logger.success(f"Fetched Chart from cache")
        return {"status": "cached", "data": chart_data}

    # Step 2: Full generation pipeline

    pipeline2 = chain(
        lookup_log_registry.s(log_id),
        get_log_dispatch_chart.s(chart_name),
    )
    result2 = pipeline2.apply_async()
    chart_data = result2.get(timeout=60)


    if chart_data is not None:
        logger.success(f"Chart generated from log")
        post_pipeline = chain(
            store_chart_json_in_s3.s(log_id, chart_name, chart_data),
            log_chart_in_registry.s(),
        )
        post_pipeline.apply_async()
        return {"status": "generated", "data": chart_data}
    elif chart_data is None:
        topic_name = CHART_REGISTRY.get(chart_name).topic_name
        logger.warning(f"Chart data is None for log_id: {log_id}, chart_name: {chart_name}")
        return {"status": "topic_not_found", "data": chart_data, "topic_name": topic_name}
    # run pipeline3 aafter sending the result above

    logger.error(
        f"Failed to find or generate a chart: {chart_name} for log_id: {log_id}, total time spent: {et1 + et2:.2f} seconds"
    )
    return {"status": None, "data": chart_data}
