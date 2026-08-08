from __future__ import annotations

from dataclasses import dataclass

from src.core.kpi import KPI
from src.core.telemetry_session import TelemetrySession
from src.database.models.kpi import KPIModel
from src.database.models.race_session import RaceSessionModel
from src.database.session_factory import SessionFactory


@dataclass(frozen=True)
class PersistenceResult:
    race_session_id: int
    kpi_count: int


class AnalysisPersistenceService:
    """
    Persist an analysed telemetry session and its engineering KPIs.

    The entire operation is transactional:
    - create race session;
    - obtain its database ID;
    - create associated KPIs;
    - commit everything together.

    If any operation fails, SessionFactory.session_scope()
    rolls the transaction back.
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
        """
        Save one telemetry analysis and its KPIs.
        """

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
            race_session_model = RaceSessionModel(
                name=resolved_session_name,
                session_type=session_type,
                source_file=telemetry_session.filename,
                source_system=telemetry_session.source_system,
            )

            session.add(
                race_session_model
            )

            # We need the generated primary key before
            # inserting KPI records.
            session.flush()

            if race_session_model.id is None:
                raise RuntimeError(
                    "Database did not generate a race-session ID."
                )

            race_session_id = int(
                race_session_model.id
            )

            for kpi in kpis:
                model = KPIModel(
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

                session.add(model)

            # Optional, but makes DB failures happen here,
            # before leaving the transaction context.
            session.flush()

        return PersistenceResult(
            race_session_id=race_session_id,
            kpi_count=len(kpis),
        )

    @staticmethod
    def _flatten_kpis(
        kpi_results: dict[str, list[KPI]],
    ) -> list[KPI]:
        kpis: list[KPI] = []

        for category_kpis in kpi_results.values():
            kpis.extend(
                category_kpis
            )

        return kpis

    @staticmethod
    def _default_session_name(
        telemetry_session: TelemetrySession,
    ) -> str:
        stem = telemetry_session.source_file.stem

        return stem or "Telemetry Session"