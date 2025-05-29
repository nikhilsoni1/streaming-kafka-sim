from celery import Celery
from render_rig2.utils.config import CELERY_CONFIG

# Initialize the Celery app
celery_app = Celery("render_rig2")
celery_app.config_from_object(CELERY_CONFIG)

# Auto-discover tasks from the celery_app.tasks package
celery_app.autodiscover_tasks(["render_rig2.tasks_v2"])


# celery -A render_rig2.app_v2 worker -Q lookup_chart_registry,get_existing_chart,lookup_log_registry,get_log_dispatch_chart,store_log_chart -c 6 --loglevel=info