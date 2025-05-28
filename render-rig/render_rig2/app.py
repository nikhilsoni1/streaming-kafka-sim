from celery import Celery
from render_rig2.utils.config import CELERY_CONFIG
from celery.signals import setup_logging
from render_rig2.utils.logger import logger

# Initialize the Celery app
celery_app = Celery("render_rig2")
celery_app.config_from_object(CELERY_CONFIG)

# Auto-discover tasks from the celery_app.tasks package
celery_app.autodiscover_tasks(["render_rig2.tasks"])

