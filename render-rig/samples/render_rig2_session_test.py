from render_rig2.database_access.sessions import RenderRigSessionLocal
from render_rig2.database_access.sessions import LogRegistrySessionLocal
from render_rig2.utils.logger import logger
from sqlalchemy import text
from time import perf_counter

# Test the connection
try:
    start_time = perf_counter()
    with RenderRigSessionLocal() as session:
        session.execute(text("SELECT 1"))
    end_time = perf_counter()
    elapsed_time = end_time - start_time
    logger.info(
        f"✅ RENDER RIG DB connection test successful in {elapsed_time:.2f} seconds."
    )
except Exception as e:
    logger.error(f"❌ RENDER RIG DB connection test failed: {e}")

try:
    start_time2 = perf_counter()
    with LogRegistrySessionLocal() as session:
        session.execute(text("SELECT 1"))
    end_time2 = perf_counter()
    elapsed_time2 = end_time2 - start_time2
    logger.info(
        f"✅ LOG REGISTRY DB connection test successful in {elapsed_time2:.2f} seconds."
    )
except Exception as e:
    logger.error(f"❌ LOG REGISTRY DB connection test failed: {e}")
