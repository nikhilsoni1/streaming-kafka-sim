import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from render_rig2.utils.timing import timed_debug_log

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

with timed_debug_log("RENDER RIG SQLAlchemy Engine creation"):
    RENDER_RIG_DB_ENGINE = create_engine(
        RENDER_RIG_DB_URL,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
    )

with timed_debug_log("RENDER RIG SQLAlchemy SessionLocal factory initialization"):
    RenderRigSessionLocal = sessionmaker(
        bind=RENDER_RIG_DB_ENGINE,
        autoflush=False,
        autocommit=False,
    )
