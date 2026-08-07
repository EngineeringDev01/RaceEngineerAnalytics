from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class SessionFactory:
    """
    Central SQLAlchemy engine and session factory.

    Responsibilities:
    - create the SQLAlchemy engine;
    - create database sessions;
    - manage transaction lifecycle;
    """

    def __init__(
        self,
        database_url: str,
        echo: bool = False,
    ) -> None:
        self.database_url = database_url

        self.engine: Engine = create_engine(
            database_url,
            echo=echo,
            future=True,
            pool_pre_ping=True,
        )

        self._session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
        )

    def create_session(self) -> Session:
        """
        Create a new SQLAlchemy Session.

        Caller is responsible for closing it.
        """
        return self._session_factory()

    @contextmanager
    def session_scope(
        self,
    ) -> Generator[Session, None, None]:
        """
        Provide a transactional session scope.

        Automatically:
        - commits successful transactions;
        - rolls back failures;
        - closes the session.
        """
        session = self.create_session()

        try:
            yield session
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def dispose(self) -> None:
        """
        Release SQLAlchemy connection-pool resources.
        """
        self.engine.dispose()