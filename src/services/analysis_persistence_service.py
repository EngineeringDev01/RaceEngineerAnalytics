from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy import select

from src.core.kpi import KPI
from src.core.telemetry_session import TelemetrySession
from src.database.models.kpi import KPIModel
from src.database.models.race_session import RaceSessionModel
from src.database.session_factory import SessionFactory


class DuplicateAnalysisError(RuntimeError):
    """
    Raised when telemetry has already been persisted.
    """

    def __init__(
        self,
        race_session_id: int,
        file_hash: str,
    ) -> None:
        self.race_session_id = race_session_id
        self.file_hash = file_hash

        super().__init__(
            "This telemetry file has already been saved "
            f"as race session ID {race_session_id}."
        )


@dataclass(frozen=True)
class PersistenceResult:
    race_session_id: int
    kpi_count: int
    file_hash: str


class AnalysisPersistenceService:
    """
    Persist analysed telemetry and calculated KPIs.

    A SHA-256 fingerprint prevents accidental duplicate
    insertion of the same telemetry file.
    """

    def __init__(
        self,
        session_factory: SessionFactory,
    ) -> None:
        self.session_factory = session_factory

    def save_analysis(
        self,
        telemetry_session: TelemetrySession,
        kpi_results: dict[str, list[KPI]],
        session_name: str | None = None,
        session_type: str = "other",
    ) -> PersistenceResult:
        file_hash = self._calculate_file_hash(
            telemetry_session
        )

        resolved_session_name = (
            session_name
            or self._default_session_name(
                telemetry_session
            )
        )

        kpis = self._flatten_kpis(
            kpi_results
        )

        with self.session_factory.session_scope() as session:
            existing = session.scalar(
                select(RaceSessionModel)
                .where(
                    RaceSessionModel.file_hash
                    == file_hash
                )
            )

            if existing is not None:
                raise DuplicateAnalysisError(
                    race_session_id=existing.id,
                    file_hash=file_hash,
                )

            race_session_model = RaceSessionModel(
                name=resolved_session_name,
                session_type=session_type,
                source_file=telemetry_session.filename,
                source_system=telemetry_session.source_system,
                file_hash=file_hash,
            )

            session.add(
                race_session_model
            )

            session.flush()

            if race_session_model.id is None:
                raise RuntimeError(
                    "Database did not generate "
                    "a race-session ID."
                )

            race_session_id = int(
                race_session_model.id
            )

            for kpi in kpis:
                kpi_model = KPIModel(
                    race_session_id=race_session_id,
                    category=kpi.category,
                    name=kpi.name,
                    value=(
                        float(kpi.value)
                        if kpi.value is not None
                        else None
                    ),
                    unit=kpi.unit,
                    source_channel=kpi.source_channel,
                    description=kpi.description,
                )

                session.add(
                    kpi_model
                )

            session.flush()

        return PersistenceResult(
            race_session_id=race_session_id,
            kpi_count=len(kpis),
            file_hash=file_hash,
        )

    def analysis_exists(
        self,
        telemetry_session: TelemetrySession,
    ) -> bool:
        file_hash = self._calculate_file_hash(
            telemetry_session
        )

        with self.session_factory.session_scope() as session:
            statement = (
                select(RaceSessionModel.id)
                .where(
                    RaceSessionModel.file_hash
                    == file_hash
                )
            )

            return (
                session.scalar(statement)
                is not None
            )

    def find_existing_session_id(
        self,
        telemetry_session: TelemetrySession,
    ) -> int | None:
        file_hash = self._calculate_file_hash(
            telemetry_session
        )

        with self.session_factory.session_scope() as session:
            statement = (
                select(RaceSessionModel.id)
                .where(
                    RaceSessionModel.file_hash
                    == file_hash
                )
            )

            result = session.scalar(
                statement
            )

            return (
                int(result)
                if result is not None
                else None
            )

    def recent_sessions(
        self,
        limit: int = 10,
    ) -> list[dict]:
        with self.session_factory.session_scope() as session:
            models = session.scalars(
                select(RaceSessionModel)
                .order_by(
                    RaceSessionModel.created_at.desc()
                )
                .limit(limit)
            ).all()

            return [
                {
                    "id": model.id,
                    "name": model.name,
                    "type": model.session_type,
                    "source": model.source_system,
                    "file": model.source_file,
                    "created_at": model.created_at,
                }
                for model in models
            ]

    @staticmethod
    def _calculate_file_hash(
        telemetry_session: TelemetrySession,
    ) -> str:
        source_file = (
            telemetry_session.source_file
        )

        if not source_file.exists():
            raise FileNotFoundError(
                f"Telemetry source file not found: "
                f"{source_file}"
            )

        sha256 = hashlib.sha256()

        with source_file.open("rb") as file:
            while True:
                block = file.read(
                    1024 * 1024
                )

                if not block:
                    break

                sha256.update(block)

        return sha256.hexdigest()

    @staticmethod
    def _flatten_kpis(
        kpi_results: dict[str, list[KPI]],
    ) -> list[KPI]:
        return [
            kpi
            for category in kpi_results.values()
            for kpi in category
        ]

    @staticmethod
    def _default_session_name(
        telemetry_session: TelemetrySession,
    ) -> str:
        return (
            telemetry_session.source_file.stem
            or "Telemetry Session"
        )