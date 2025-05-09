CELERY_CONFIG = {
    "broker_url": "redis://localhost:6379/0",
    "result_backend": "redis://localhost:6379/1",
    "task_default_queue": "default",
    "worker_prefetch_multiplier": 1,
    "task_routes": {
        "render_rig2.tasks.lookup_chart_registry.*": {"queue": "lookup_chart_registry"},
        "render_rig2.tasks.get_existing_chart.*": {"queue": "get_existing_chart"},
        "render_rig2.tasks.lookup_log_registry.*": {"queue": "lookup_log_registry"},
        "render_rig2.tasks.get_log_dispatch_chart.*": {"queue": "get_log_dispatch_chart"},
        "render_rig2.tasks.store_chart_json_in_s3.*": {"queue": "store_log_chart"},
        "render_rig2.tasks.log_chart_in_registry.*": {"queue": "store_log_chart"},
    }
}
