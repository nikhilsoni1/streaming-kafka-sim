# ypr_data_connector/database/base_client.py

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class BaseDatabaseClient(ABC):
    """
    Abstract base class for database clients. This class defines the interface 
    that all database client implementations must adhere to.
    """

    @abstractmethod
    def get_session(self) -> Session:
        """
        Create and return a new database session.

        Returns:
            Session: A new SQLAlchemy session object for interacting with the database.
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to the database.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        pass
