# ypr_data_connector/database/postgres_client.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base_client import BaseDatabaseClient

class PostgresDatabaseClient(BaseDatabaseClient):
    """
    A client for interacting with a PostgreSQL database using SQLAlchemy.

    This class provides methods to initialize a database connection, create sessions,
    and test the connection to the database.
    """

    def __init__(
        self,
        database_user: str,
        database_password: str,
        database_host: str,
        database_port,
        database_name: str,
    ):
        """
        Initialize the PostgresDatabaseClient with database connection details.

        Args:
            database_user (str): The username for the database.
            database_password (str): The password for the database.
            database_host (str): The host address of the database.
            database_port (int or str): The port number of the database.
            database_name (str): The name of the database.
        """
        self.database_user = database_user
        self.database_password = database_password
        self.database_host = database_host
        self.database_port = str(database_port)
        self.database_name = database_name

        self._init_engine_and_session()

    def _init_engine_and_session(self):
        """
        Initialize the SQLAlchemy engine and session maker.

        This method constructs the database URL and sets up the SQLAlchemy engine
        and session factory for database interactions.
        """
        db_url = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        self.engine = create_engine(db_url, echo=False, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_session(self) -> Session:
        """
        Create and return a new SQLAlchemy session.

        Returns:
            Session: A new SQLAlchemy session for interacting with the database.
        """
        return self.SessionLocal()

    def test_connection(self) -> bool:
        """
        Test the connection to the PostgreSQL database.

        This method attempts to execute a simple query to verify the connection.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print("Database connection failed:", e)
            return False
