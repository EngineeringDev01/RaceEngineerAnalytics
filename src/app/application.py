from __future__ import annotations

from pathlib import Path

from src.analysis.kpi_engine import KPIEngine
from src.app.container import ServiceContainer
from src.core.telemetry_session import TelemetrySession
from src.services.kpi_export_service import KPIExportService
from src.services.telemetry_service import TelemetryService


class Application:
    """
    Main application entry point.

    This class coordinates application services without depending on
    Streamlit, Plotly, MySQL, or any other user-interface technology.
    """

    def __init__(
        self,
        container: ServiceContainer | None = None,
    ) -> None:
        self.container = (
            container
            if container is not None
            else ServiceContainer()
        )

    @property
    def telemetry_service(self) -> TelemetryService:
        return self.container.telemetry_service

    @property
    def kpi_export_service(self) -> KPIExportService:
        return self.container.kpi_export_service

    def load_telemetry(
        self,
        file_path: str | Path,
    ) -> TelemetrySession:
        """
        Load and validate telemetry through the application service layer.
        """
        return self.telemetry_service.load(
            file_path
        )

    @staticmethod
    def create_kpi_engine(
        session: TelemetrySession,
    ) -> KPIEngine:
        """
        Create a KPI engine for an imported telemetry session.

        The KPI engine currently depends on a specific session and is
        therefore created per analysis operation rather than shared.
        """
        return KPIEngine(session)

    def calculate_kpis(
        self,
        session: TelemetrySession,
    ) -> dict:
        """
        Calculate all currently supported engineering KPIs.
        """
        engine = self.create_kpi_engine(
            session
        )

        return engine.calculate()