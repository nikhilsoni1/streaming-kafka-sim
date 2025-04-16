from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


class DatabaseClient:
    def __init__(
        self,
        database_user: str,
        database_password: str,
        database_host: str,
        database_port,
        database_name: str,
    ):
        """
        Initialize the database connection and session factory.

        Args:
            database_user (str): Database username.
            database_password (str): Database password.
            database_host (str): Database host.
            database_port (int | str): Database port.
            database_name (str): Database name.
        """
        self.database_user = database_user
        self.database_password = database_password
        self.database_host = database_host
        self.database_port = str(database_port)
        self.database_name = database_name

        self._init_engine_and_session()

    def _init_engine_and_session(self):
        db_url = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        self.engine = create_engine(db_url, echo=False, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_session(self) -> Session:
        """
        Get a new SQLAlchemy session.

        Returns:
            Session: A SQLAlchemy session.
        """
        return self.SessionLocal()

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print("Database connection failed:", e)
            return False
