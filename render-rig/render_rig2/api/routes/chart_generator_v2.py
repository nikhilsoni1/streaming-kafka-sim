import os
import uuid
from fastapi import APIRouter
from fastapi import JSONResponse
from celery import chain
from render_rig2.utils.logger import logger
from render_rig2.tasks_v2 import lookup_log_registry
from render_rig2.tasks_v2 import lookup_chart_registry
from render_rig2.tasks_v2 import get_existing_chart
from render_rig2.tasks_v2 import get_log_dispatch_chart
from render_rig2.tasks_v2 import log_chart_in_registry
from render_rig2.tasks_v2 import store_chart_json_in_s3

router = APIRouter()

@router.post("/{log_id}/{chart_name}")
async def generate_chart_v2(log_id: str, chart_name: str):
    """
    NEW async-first chart generation endpoint.
    Will support:
    - 202 Accepted
    - Redis task status tracking
    - optional webhook delivery
    """
    task_id = str(uuid.uuid4().hex)
    webhook_url = get_webhook_url(task_id)

    payload_dict = {
        "log_id": log_id,
        "chart_name": chart_name,
        "webhook_url": webhook_url,
        "task_id": task_id,
    }
    
    pipeline = chain(
    lookup_chart_registry.s(payload_dict),
    get_existing_chart.s(),
    lookup_log_registry.s(),
    get_log_dispatch_chart.s(),
    store_chart_json_in_s3.s(),
    log_chart_in_registry.s(),
    )
    pipeline.delay()

    return JSONResponse(status_code=202, content={"task_id": task_id})
    # return {"status": None, "data": chart_data}