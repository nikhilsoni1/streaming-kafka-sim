from ypr_data_connector.database_client import PostgresDatabaseClient
from render_rig.data_access.database.models import LogsDlReg
import os

def get_log_registry_session() -> PostgresDatabaseClient:
    database_user = os.environ["DATABASE_USER"]
    database_password = os.environ["DATABASE_PASSWORD"]
    database_host = os.environ["DATABASE_HOST"]
    database_port = os.environ["DATABASE_PORT"]
    log_registry_database_name = os.environ.get("LOG_REGISTRY_DATABASE_NAME")

    postgres_client = PostgresDatabaseClient(
        database_host=database_host,
        database_port=database_port,
        database_user=database_user,
        database_password=database_password,
        database_name=log_registry_database_name,
    )
    if postgres_client.test_connection():
        print("Postgres connection successful")
        return postgres_client.get_session()
    else:
        print("Postgres connection failed")
        raise Exception("Postgres connection failed")

def get_file3path_from_logregistry(log_id: str) -> str:
    """
    Get the S3 URI for a given log ID from the database.

    :param log_id: The log ID to query.
    :return: The S3 URI associated with the log ID.
    """
    session = get_log_registry_session()
    result = (
    session.query(LogsDlReg.file_s3_path)
    .filter(LogsDlReg.log_id == log_id)
    .one_or_none()
    )
    session.close()
    return result[0] if result else None

if __name__ == "__main__":
    from render_rig.data_access.object_access import s3_get_object_by_uri
    # Example usage
    log_id = "a224339a-2537-480d-990e-1e30197ee72e"
    s3_uri = get_file3path_from_logregistry(log_id)
    if s3_uri:
        print(f"S3 URI for log ID {log_id}: {s3_uri}")
        cache_path = s3_get_object_by_uri(s3_uri=s3_uri, region_name="us-east-1", mode="cache")
        print(cache_path)

    else:
        print(f"No S3 URI found for log ID {log_id}")


