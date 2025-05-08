# render_rig2/utils/logger.py

from loguru import logger
from rich.console import Console
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Clear previous handlers
logger.remove()

# Add rich console sink
logger.add(
    Console().print,
    level="DEBUG",  # Can be made dynamic
    format="[bold cyan]{time:HH:mm:ss}[/] | [bold magenta]{level}[/] | [green]{module}:{function}:{line}[/] - {message}",
)

# Add file sink
logger.add(
    LOG_FILE,
    rotation="1 MB",
    retention="7 days",
    compression="zip",
    level="INFO",  # File sink can be more restrictive
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} | {message}",
)

# ✅ Add this helper
def is_debug_enabled() -> bool:
    # Return True if any sink is set to DEBUG or lower
    return any(
        sink.levelno <= logger.level("DEBUG").no
        for sink in logger._core.handlers.values()
    )
