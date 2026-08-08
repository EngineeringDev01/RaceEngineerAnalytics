from __future__ import annotations

from abc import abstractmethod

from src.database.repositories.base import Repository
from src.domain.race_session import RaceSession


class RaceSessionRepository(
    Repository[RaceSession, int]
):
    @abstractmethod
    def find_by_name(
        self,
        name: str,
    ) -> list[RaceSession]:
        raise NotImplementedError

    @abstractmethod
    def find_by_session_type(
        self,
        session_type: str,
    ) -> list[RaceSession]:
        raise NotImplementedError