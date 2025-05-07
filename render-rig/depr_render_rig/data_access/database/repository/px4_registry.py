from ypr_data_connector.database_client import PostgresDatabaseClient
from depr_render_rig.data_access.database.models.px4_registry_model import LogsDlReg
from sqlalchemy.orm import Session

def get_s3uri_from_logregistry(log_id: str, session: Session) -> str:
    """
    Get the S3 URI for a given log ID from the database.

    :param log_id: The log ID to query.
    :return: The S3 URI associated with the log ID.
    """
    result = (
    session.query(LogsDlReg.file_s3_path)
    .filter(LogsDlReg.log_id == log_id)
    .one_or_none()
    )
    session.close()
    return result[0] if result else None

if __name__ == "__main__":
    pass


