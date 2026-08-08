from __future__ import annotations

from sqlalchemy import text

from src.database.base import Base
from src.database.manager import DatabaseManager
from src.database.session_factory import SessionFactory

# Import ORM models so they are registered in Base.metadata.
from src.database import models  # noqa: F401


class SQLAlchemyDatabaseManager(DatabaseManager):
    """
    SQLAlchemy implementation of the generic DatabaseManager interface.
    """

    def __init__(
        self,
        session_factory: SessionFactory,
    ) -> None:
        self.session_factory = session_factory
        self._connected = False

    def connect(self) -> None:
        with self.session_factory.engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        self._connected = True

    def disconnect(self) -> None:
        self.session_factory.dispose()
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def create_schema(self) -> None:
        Base.metadata.create_all(
            self.session_factory.engine
        )

    def drop_schema(self) -> None:
        Base.metadata.drop_all(
            self.session_factory.engine
        )