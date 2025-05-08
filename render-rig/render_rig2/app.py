from celery import Celery
from render_rig2.utils.config import CELERY_CONFIG
from celery.signals import setup_logging
from render_rig2.utils.logger import logger

# Initialize the Celery app
celery_app = Celery("render_rig2")
celery_app.config_from_object(CELERY_CONFIG)

# Auto-discover tasks from the celery_app.tasks package
celery_app.autodiscover_tasks(["render_rig2.tasks"])


@setup_logging.connect
def setup_celery_logging(**kwargs):
    import logging

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Redirect all standard logging to loguru
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())

    # Patch the Celery logger
    logging.getLogger("celery").handlers = [InterceptHandler()]
    logging.getLogger("celery").setLevel(logging.DEBUG)
