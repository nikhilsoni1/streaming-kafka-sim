# session.py
import os
from ypr_data_connector.database_client import PostgresDatabaseClient

_clients = {}

def _create_client(name: str, env_map: dict) -> PostgresDatabaseClient:
    return PostgresDatabaseClient(
        database_host=os.environ[env_map["HOST"]],
        database_port=os.environ[env_map["PORT"]],
        database_user=os.environ[env_map["USER"]],
        database_password=os.environ[env_map["PASS"]],
        database_name=os.environ[env_map["NAME"]],
    )

def _get_or_create_client(name: str, env_map: dict) -> PostgresDatabaseClient:
    if name not in _clients:
        client = _create_client(name, env_map)
        if not client.test_connection():
            raise ConnectionError(f"Connection to {name} DB failed.")
        _clients[name] = client
    return _clients[name]

# 🎯 Explicit DB session factories
def get_render_rig_session():
    render_rig_env_map = {
        "HOST": "RENDER_RIG_DB_HOST",
        "PORT": "RENDER_RIG_DB_PORT",
        "USER": "RENDER_RIG_DB_USER",
        "PASS": "RENDER_RIG_DB_PASS",
        "NAME": "RENDER_RIG_DB_NAME"
    }
    return _get_or_create_client("render_rig", render_rig_env_map).get_session()

def get_log_registry_session():
    log_registry_env_map = {
        "HOST": "LOG_REGISTRY_DB_HOST",
        "PORT": "LOG_REGISTRY_DB_PORT",
        "USER": "LOG_REGISTRY_DB_USER",
        "PASS": "LOG_REGISTRY_DB_PASS",
        "NAME": "LOG_REGISTRY_DB_NAME"
    }
    return _get_or_create_client("log_registry", log_registry_env_map).get_session()
