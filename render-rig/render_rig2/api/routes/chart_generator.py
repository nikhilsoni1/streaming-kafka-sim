from fastapi import APIRouter
from celery import chain
from render_rig2.tasks import lookup_log_registry
from render_rig2.tasks import lookup_chart_registry
from render_rig2.tasks import get_existing_chart
from render_rig2.tasks import get_log_dispatch_chart
from render_rig2.tasks import log_chart_in_registry
from render_rig2.tasks import store_chart_json_in_s3
from render_rig2.utils.logger import logger
from render_rig2.chart_engine import CHART_REGISTRY
from time import perf_counter

router = APIRouter()


@router.get("/", summary="List available chart types")
def list_charts():
    return list(CHART_REGISTRY.keys())

@router.get("/{log_id}/{chart_name}")
async def generate_chart(log_id: str, chart_name: str):
    # double check chart_json type
    """
    Generate a chart for a given log_id and chart_name.
    """
    logger.debug(f"Generating chart for log_id: {log_id}, chart_name: {chart_name}")
    chart_data = None

    t0 = perf_counter()

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

    t1 = perf_counter()
    et1 = t1 - t0

    if chart_data is not None:
        logger.success(f"Chart from cache returned in {et1:.2f} seconds")
        return {"status": "cached", "data": chart_data}

    # Step 2: Full generation pipeline
    t2 = perf_counter()

    pipeline2 = chain(
        lookup_log_registry.s(log_id),
        get_log_dispatch_chart.s(chart_name),
    )
    result2 = pipeline2.apply_async()
    chart_data = result2.get(timeout=60)

    t3 = perf_counter()
    et2 = t3 - t2

    if chart_data is not None:
        logger.success(f"Chart generated from log returned in {et2:.2f} seconds")
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


#   after return to fastapi, store in s3 and update the chart registry
