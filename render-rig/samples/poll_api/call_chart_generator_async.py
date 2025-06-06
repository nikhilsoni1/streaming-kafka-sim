import asyncio
import aiohttp
import random
from render_rig2.utils.logger import logger
from render_rig2.database_access.sessions.log_registry_session_local import LogRegistrySessionLocal
from render_rig2.database_access.sessions.render_rig_session_local import RenderRigSessionLocal
from render_rig2.database_access.models.log_registry_model import LogsDlReg
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Generator


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


async def call_chart_generator_endpoint(session, log_id: str, chart_name: str):
    url = f"http://localhost:8000/chart_generator/{log_id}/{chart_name}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            size_mb = len(await response.text()) / (1024 * 1024)
            print(f"Chart Status: {data.get('status')}, Size: {size_mb:.2f} MB")
    except Exception as e:
        print(f"Error fetching {url}: {e}")


async def main():
    chart_name = "chart_accel_raw_xyz"

    db1 = LogRegistrySessionLocal()
    gen1 = random_log_id_generator(db1)

    db2 = RenderRigSessionLocal()
    gen2 = random_log_id_from_chart_registry_generator(db2)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(10):
            log_id = next(gen1 if random.choice([True, False]) else gen2)
            print(f"Scheduling chart generation for log_id: {log_id}")
            tasks.append(call_chart_generator_endpoint(session, log_id, chart_name))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
