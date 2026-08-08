from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")
ID = TypeVar("ID")


class Repository(
    ABC,
    Generic[T, ID],
):
    @abstractmethod
    def add(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def get(self, entity_id: ID) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: ID) -> bool:
        raise NotImplementedError