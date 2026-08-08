from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models.race_session import RaceSessionModel
from src.database.repositories.session_repository import RaceSessionRepository
from src.domain.car import Car
from src.domain.race_session import RaceSession, SessionType


class SQLAlchemyRaceSessionRepository(
    RaceSessionRepository
):
    """SQLAlchemy implementation of the race-session repository."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def add(
        self,
        entity: RaceSession,
    ) -> RaceSession:
        source_file = None
        source_system = None

        if entity.telemetry_sessions:
            telemetry = entity.telemetry_sessions[0]

            source_file = telemetry.filename
            source_system = telemetry.source_system

        model = RaceSessionModel(
            name=entity.name,
            session_type=entity.session_type.value,
            source_file=source_file,
            source_system=source_system,
        )

        self.session.add(model)
        self.session.flush()

        return entity

    def get(
        self,
        entity_id: int,
    ) -> RaceSession | None:
        model = self.session.get(
            RaceSessionModel,
            entity_id,
        )

        if model is None:
            return None

        return self._to_domain(model)

    def list_all(
        self,
    ) -> list[RaceSession]:
        models = self.session.scalars(
            select(RaceSessionModel)
            .order_by(RaceSessionModel.id)
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
            RaceSessionModel,
            entity_id,
        )

        if model is None:
            return False

        self.session.delete(model)
        self.session.flush()

        return True

    def find_by_name(
        self,
        name: str,
    ) -> list[RaceSession]:
        models = self.session.scalars(
            select(RaceSessionModel)
            .where(
                RaceSessionModel.name == name
            )
            .order_by(RaceSessionModel.id)
        ).all()

        return [
            self._to_domain(model)
            for model in models
        ]

    def find_by_session_type(
        self,
        session_type: str,
    ) -> list[RaceSession]:
        models = self.session.scalars(
            select(RaceSessionModel)
            .where(
                RaceSessionModel.session_type
                == session_type
            )
            .order_by(RaceSessionModel.id)
        ).all()

        return [
            self._to_domain(model)
            for model in models
        ]

    @staticmethod
    def _to_domain(
        model: RaceSessionModel,
    ) -> RaceSession:
        try:
            session_type = SessionType(
                model.session_type
            )

        except ValueError:
            session_type = SessionType.OTHER

        placeholder_car = Car(
            manufacturer="Unknown",
            model="Unknown",
            category="Unknown",
        )

        return RaceSession(
            name=model.name,
            session_type=session_type,
            car=placeholder_car,
            start_time=model.created_at,
        )