import os

# Broker
CELERY_BROKER_HOST = os.getenv("CELERY_BROKER_HOST")
CELERY_BROKER_PORT = os.getenv("CELERY_BROKER_PORT")
CELERY_BROKER_DB = os.getenv("CELERY_BROKER_DB")

# Result Backend
CELERY_BACKEND_HOST = os.getenv("CELERY_BACKEND_HOST")
CELERY_BACKEND_PORT = os.getenv("CELERY_BACKEND_PORT")
CELERY_BACKEND_DB = os.getenv("CELERY_BACKEND_DB")

CELERY_CONFIG = {
    "broker_url": f"redis://{CELERY_BROKER_HOST}:{CELERY_BROKER_PORT}/{CELERY_BROKER_DB}",
    "result_backend": f"redis://{CELERY_BACKEND_HOST}:{CELERY_BACKEND_PORT}/{CELERY_BACKEND_DB}",
    "task_default_queue": "default",
    "worker_prefetch_multiplier": 1,
    "task_routes": {
        "lookup_chart_registry": {"queue": "lookup_chart_registry"},
        "get_existing_chart": {"queue": "get_existing_chart"},
        "lookup_log_registry": {"queue": "lookup_log_registry"},
        "get_log_dispatch_chart": {"queue": "get_log_dispatch_chart"},
        "store_chart_json_in_s3": {"queue": "store_log_chart"},
        "log_chart_in_registry": {"queue": "store_log_chart"},
    }
}
