from __future__ import annotations

from pathlib import Path

from src.analysis.kpi_engine import KPIEngine
from src.app.container import ServiceContainer
from src.app.settings import Settings, SettingsLoader
from src.core.telemetry_session import TelemetrySession
from src.services.kpi_export_service import KPIExportService
from src.services.telemetry_service import TelemetryService


class Application:
    """
    Main application entry point.
    """

    def __init__(
        self,
        container: ServiceContainer | None = None,
        config_path: str | Path | None = None,
    ) -> None:
        if container is not None:
            self.container = container
            return

        project_root = Path(__file__).resolve().parents[2]

        resolved_config_path = (
            Path(config_path)
            if config_path is not None
            else project_root / "config" / "config.yaml"
        )

        settings = SettingsLoader(
            resolved_config_path
        ).load()

        self.container = ServiceContainer(
            settings=settings
        )

    @property
    def settings(self) -> Settings:
        return self.container.settings

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
        return self.telemetry_service.load(
            file_path
        )

    def create_kpi_engine(
        self,
        session: TelemetrySession,
    ) -> KPIEngine:
        return KPIEngine(
            session=session,
            full_throttle_threshold_pct=(
                self.settings.engineering
                .full_throttle_threshold_pct
            ),
            brake_active_threshold_bar=(
                self.settings.engineering
                .brake_active_threshold_bar
            ),
        )

    def calculate_kpis(
        self,
        session: TelemetrySession,
    ) -> dict:
        return self.create_kpi_engine(
            session
        ).calculate()