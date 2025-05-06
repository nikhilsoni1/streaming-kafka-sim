CELERY_CONFIG = {
    "broker_url": "redis://localhost:6379/0",
    "result_backend": "redis://localhost:6379/1",
    "task_routes": {
        "celery_app.tasks.ingest.*": {"queue": "ingest"},
        "celery_app.tasks.db_writer.*": {"queue": "db_writer"},
        "celery_app.tasks.export.*": {"queue": "export"},
    },
    "task_default_queue": "default",
    "worker_prefetch_multiplier": 1,
}
