import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from time import perf_counter
from render_rig2.utils.logger import logger

# ------------------------------------------
# Load environment variables for RENDER RIG
# ------------------------------------------
RENDER_RIG_DB_NAME = os.getenv("RENDER_RIG_DB_NAME")
RENDER_RIG_DB_USER = os.getenv("RENDER_RIG_DB_USER")
RENDER_RIG_DB_PASS = os.getenv("RENDER_RIG_DB_PASS")
RENDER_RIG_DB_HOST = os.getenv("RENDER_RIG_DB_HOST")
RENDER_RIG_DB_PORT = os.getenv("RENDER_RIG_DB_PORT")

RENDER_RIG_DB_URL = (
    f"postgresql+psycopg2://{RENDER_RIG_DB_USER}:{RENDER_RIG_DB_PASS}@"
    f"{RENDER_RIG_DB_HOST}:{RENDER_RIG_DB_PORT}/{RENDER_RIG_DB_NAME}"
)

# ⏱ Time the engine creation
start_engine_rig = perf_counter()
RENDER_RIG_DB_ENGINE = create_engine(
    RENDER_RIG_DB_URL,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)
end_engine_rig = perf_counter()
logger.info(
    f"🚀 RENDER RIG SQLAlchemy Engine created in {round(end_engine_rig - start_engine_rig, 4)}s"
)

# ⏱ Time the session factory setup
start_session_rig = perf_counter()
RenderRigSessionLocal = sessionmaker(
    bind=RENDER_RIG_DB_ENGINE,
    autoflush=False,
    autocommit=False,
)
end_session_rig = perf_counter()
logger.info(
    f"🔧 RENDER RIG SessionLocal factory initialized in {round(end_session_rig - start_session_rig, 4)}s"
)
