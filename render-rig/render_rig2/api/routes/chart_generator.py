from fastapi import APIRouter
from celery import chain
from render_rig2.tasks import lookup_log_registry
from render_rig2.tasks import lookup_chart_registry
from render_rig2.tasks import get_existing_chart
from render_rig2.tasks import get_log_dispatch_chart
from render_rig2.utils.logger import logger

router = APIRouter()

@router.get("/{log_id}/{chart_name}")
async def generate_chart(log_id: str, chart_name: str):
    chart_data = None
    task_lookup_chart_registry = lookup_chart_registry.delay(log_id, chart_name)
    result = task_lookup_chart_registry.get(timeout=10)
    if result is not None:
        task_get_existing_chart = get_existing_chart.delay(result)
        chart_data = task_get_existing_chart.get(timeout=10)
        chart_data = chart_data.decode("utf-8")

    if chart_data is not None:
        payload = {"status": "cached", "data": chart_data}
        logger.info(f"Chart data type: {type(chart_data)}")
        return payload

    # Step 2: Full generation pipeline
    pipeline = chain(
        lookup_log_registry.s(log_id),
        get_log_dispatch_chart.s(chart_name),
    )
    result = pipeline.apply_async()
    chart_data = result.get(timeout=60)
    logger.info(f"Chart data type: {type(chart_data)}")

    return {"status": "generated", "data": chart_data}
