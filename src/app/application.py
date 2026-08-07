from __future__ import annotations

import logging
from pathlib import Path

from src.analysis.kpi_engine import KPIEngine
from src.app.container import ServiceContainer
from src.app.logging import configure_logging
from src.app.settings import Settings, SettingsLoader
from src.core.telemetry_session import TelemetrySession
from src.services.kpi_export_service import KPIExportService
from src.services.telemetry_service import TelemetryService


class Application:
    """
    Main application entry point.

    The Application object coordinates:
    - configuration;
    - dependency container;
    - logging;
    - telemetry loading;
    - KPI calculation.

    User interfaces such as Streamlit or CLI should access
    application services through this class.
    """

    def __init__(
        self,
        container: ServiceContainer | None = None,
        config_path: str | Path | None = None,
    ) -> None:
        self.project_root = (
            Path(__file__).resolve().parents[2]
        )

        if container is not None:
            self.container = container

        else:
            resolved_config_path = (
                Path(config_path)
                if config_path is not None
                else (
                    self.project_root
                    / "config"
                    / "config.yaml"
                )
            )

            settings = SettingsLoader(
                resolved_config_path
            ).load()

            self.container = ServiceContainer(
                settings=settings
            )

        self.logger = self._configure_logging()

        self.logger.info(
            "Starting %s version %s",
            self.settings.application.name,
            self.settings.application.version,
        )

    @property
    def settings(self) -> Settings:
        return self.container.settings

    @property
    def telemetry_service(
        self,
    ) -> TelemetryService:
        return self.container.telemetry_service

    @property
    def kpi_export_service(
        self,
    ) -> KPIExportService:
        return self.container.kpi_export_service

    def _configure_logging(
        self,
    ) -> logging.Logger:
        log_level = getattr(
            logging,
            self.settings.logging.level.upper(),
            logging.INFO,
        )

        log_directory = (
            self.project_root
            / self.settings.logging.directory
        )

        return configure_logging(
            log_directory=log_directory,
            level=log_level,
        )

    def load_telemetry(
        self,
        file_path: str | Path,
    ) -> TelemetrySession:
        self.logger.info(
            "Loading telemetry file: %s",
            file_path,
        )

        try:
            session = self.telemetry_service.load(
                file_path
            )

        except Exception:
            self.logger.exception(
                "Telemetry import failed: %s",
                file_path,
            )
            raise

        self.logger.info(
            (
                "Telemetry loaded: "
                "source=%s samples=%s channels=%s"
            ),
            session.source_system,
            session.samples,
            len(session.channels),
        )

        return session

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
        self.logger.info(
            "Calculating KPIs for: %s",
            session.filename,
        )

        try:
            results = self.create_kpi_engine(
                session
            ).calculate()

        except Exception:
            self.logger.exception(
                "KPI calculation failed: %s",
                session.filename,
            )
            raise

        total_kpis = sum(
            len(kpis)
            for kpis in results.values()
        )

        self.logger.info(
            "KPI calculation complete: %s KPIs",
            total_kpis,
        )

        return results