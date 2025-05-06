import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from time import perf_counter
from render_rig2.logger import logger


# ----------------------------------------------
# Load environment variables for LOG REGISTRY DB
# ----------------------------------------------
LOG_REGISTRY_DB_NAME = os.getenv("LOG_REGISTRY_DB_NAME")
LOG_REGISTRY_DB_USER = os.getenv("LOG_REGISTRY_DB_USER")
LOG_REGISTRY_DB_PASS = os.getenv("LOG_REGISTRY_DB_PASS")
LOG_REGISTRY_DB_HOST = os.getenv("LOG_REGISTRY_DB_HOST")
LOG_REGISTRY_DB_PORT = os.getenv("LOG_REGISTRY_DB_PORT")

LOG_REGISTRY_DB_URL = (
    f"postgresql+psycopg2://{LOG_REGISTRY_DB_USER}:{LOG_REGISTRY_DB_PASS}@"
    f"{LOG_REGISTRY_DB_HOST}:{LOG_REGISTRY_DB_PORT}/{LOG_REGISTRY_DB_NAME}"
)

# ⏱ Time the engine creation
start_engine_log = perf_counter()
LOG_REGISTRY_DB_ENGINE = create_engine(
    LOG_REGISTRY_DB_URL,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)
end_engine_log = perf_counter()
logger.info(
    f"🚀 LOG REGISTRY SQLAlchemy Engine created in {round(end_engine_log - start_engine_log, 4)}s"
)

# ⏱ Time the session factory setup
start_session_log = perf_counter()
LogRegistrySessionLocal = sessionmaker(
    bind=LOG_REGISTRY_DB_ENGINE,
    autoflush=False,
    autocommit=False,
)
end_session_log = perf_counter()
logger.info(
    f"🔧 LOG REGISTRY SessionLocal factory initialized in {round(end_session_log - start_session_log, 4)}s"
)
