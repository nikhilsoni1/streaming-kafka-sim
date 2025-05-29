from fastapi import APIRouter
from render_rig2.utils.redis_status import get_task_status

router = APIRouter()

@router.get("/{task_id}")
async def get_status(task_id: str):
    status = get_task_status(task_id)
    if status is None:
        return {"status": "not_found"}
    return status