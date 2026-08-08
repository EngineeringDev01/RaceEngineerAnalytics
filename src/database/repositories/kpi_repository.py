from __future__ import annotations

from abc import abstractmethod

from src.core.kpi import KPI
from src.database.repositories.base import Repository


class KPIRepository(
    Repository[KPI, int]
):
    @abstractmethod
    def find_by_category(
        self,
        category: str,
    ) -> list[KPI]:
        raise NotImplementedError

    @abstractmethod
    def find_by_name(
        self,
        name: str,
    ) -> list[KPI]:
        raise NotImplementedError