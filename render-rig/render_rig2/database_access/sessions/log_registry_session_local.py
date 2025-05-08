import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from render_rig2.utils.timing import timed_debug_log


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


with timed_debug_log(f"LOG REGISTRY SQLAlchemy Engine creation"):
    # Create the SQLAlchemy engine for the LOG REGISTRY DB
    LOG_REGISTRY_DB_ENGINE = create_engine(
        LOG_REGISTRY_DB_URL,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
    )

with timed_debug_log(f"LOG REGISTRY SQLAlchemy SessionLocal factory initialization"):
    LogRegistrySessionLocal = sessionmaker(
        bind=LOG_REGISTRY_DB_ENGINE,
        autoflush=False,
        autocommit=False,
    )

