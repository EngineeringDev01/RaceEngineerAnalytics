from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.kpi import KPI
from src.database.models.kpi import KPIModel
from src.database.repositories.kpi_repository import KPIRepository


class SQLAlchemyKPIRepository(KPIRepository):
    """SQLAlchemy implementation of the KPI repository."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def add(
        self,
        entity: KPI,
        race_session_id: int | None = None,
    ) -> KPI:
        model = KPIModel(
            race_session_id=race_session_id,
            category=entity.category,
            name=entity.name,
            value=entity.value,
            unit=entity.unit,
            source_channel=entity.source_channel,
            description=entity.description,
        )

        self.session.add(model)
        self.session.flush()

        return entity

    def get(
        self,
        entity_id: int,
    ) -> KPI | None:
        model = self.session.get(
            KPIModel,
            entity_id,
        )

        if model is None:
            return None

        return self._to_domain(model)

    def list_all(self) -> list[KPI]:
        models = self.session.scalars(
            select(KPIModel)
            .order_by(KPIModel.id)
        ).all()

        return [
            self._to_domain(model)
            for model in models
        ]

    def delete(
        self,
        entity_id: int,
    ) -> bool:
        model = self.session.get(
            KPIModel,
            entity_id,
        )

        if model is None:
            return False

        self.session.delete(model)
        self.session.flush()

        return True

    def find_by_category(
        self,
        category: str,
    ) -> list[KPI]:
        models = self.session.scalars(
            select(KPIModel)
            .where(
                KPIModel.category == category
            )
            .order_by(KPIModel.id)
        ).all()

        return [
            self._to_domain(model)
            for model in models
        ]

    def find_by_name(
        self,
        name: str,
    ) -> list[KPI]:
        models = self.session.scalars(
            select(KPIModel)
            .where(
                KPIModel.name == name
            )
            .order_by(KPIModel.id)
        ).all()

        return [
            self._to_domain(model)
            for model in models
        ]

    def find_by_race_session(
        self,
        race_session_id: int,
    ) -> list[KPI]:
        models = self.session.scalars(
            select(KPIModel)
            .where(
                KPIModel.race_session_id
                == race_session_id
            )
            .order_by(KPIModel.id)
        ).all()

        return [
            self._to_domain(model)
            for model in models
        ]

    @staticmethod
    def _to_domain(
        model: KPIModel,
    ) -> KPI:
        return KPI(
            name=model.name,
            value=model.value,
            unit=model.unit,
            category=model.category,
            source_channel=model.source_channel,
            description=model.description,
        )