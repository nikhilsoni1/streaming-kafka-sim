from loguru import logger
from rich.console import Console
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Clear previous handlers
logger.remove()

# Rich console sink with colorful formatting and context
logger.add(
    Console().print,
    level="INFO",
    format="[bold cyan]{time:HH:mm:ss}[/] | [bold magenta]{level}[/] | [green]{module}:{function}:{line}[/] - {message}",
)

# File sink with detailed info
logger.add(
    LOG_FILE,
    rotation="1 MB",
    retention="7 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} | {message}",
)
