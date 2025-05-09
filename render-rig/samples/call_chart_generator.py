import requests
# from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.database_access.sessions.log_registry_session_local import LogRegistrySessionLocal
from render_rig2.database_access.sessions.render_rig_session_local import RenderRigSessionLocal
from render_rig2.database_access.models.log_registry_model import LogsDlReg
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
import random
from sqlalchemy.orm import Session
from typing import Generator
import time

def random_log_id_generator(db: Session) -> Generator[str, None, None]:
    try:
        log_ids = db.query(LogsDlReg.log_id).all()
        if not log_ids:
            logger.warning("No log_ids found in LogsDlReg")
            return

        log_ids_list = [log_id for (log_id,) in log_ids]
        while True:
            yield random.choice(log_ids_list)
    except SQLAlchemyError as e:
        logger.error("Database error during log_id fetch: %s", e)

def random_log_id_from_chart_registry_generator(db: Session) -> Generator[str, None, None]:
    try:
        log_ids = db.query(ChartRegistry.log_id).all()
        if not log_ids:
            logger.warning("No log_ids found in ChartRegistry")
            return

        log_ids_list = [log_id for (log_id,) in log_ids]
        while True:
            yield random.choice(log_ids_list)
    except SQLAlchemyError as e:
        logger.error("Database error during log_id fetch: %s", e)

def call_chart_generator_endpoint(log_id: str, chart_name: str):
    url = f"http://localhost:8000/chart_generator/{log_id}/{chart_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        print("Response Status:", response.status_code)
        # return size of response text in nearest MB
        response_size_mb = len(response.text) / (1024 * 1024)
        # response is  json and i want "status" from it
        response_json = response.json()
        print("Chart Status:", response_json.get("status"))
        print(f"Response Size: {response_size_mb:.2f} MB")
    except requests.exceptions.RequestException as e:
        print("Error while hitting the endpoint:", e)


if __name__ == "__main__":
    chart_name = "chart_accel_raw_xyz"

    db1 = LogRegistrySessionLocal()
    gen1 = random_log_id_generator(db1)

    db2 = RenderRigSessionLocal()
    gen2 = random_log_id_from_chart_registry_generator(db2)

    for _ in range(10):
        if random.choice([True, False]):
            log_id = next(gen1)
        else:
            log_id = next(gen2)
        log_id = next(gen2)
        print(f"Calling chart generator for log_id: {log_id}")
        call_chart_generator_endpoint(log_id, chart_name)
        time.sleep(1)





