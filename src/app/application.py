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
from src.core.kpi import KPI
from src.services.analysis_persistence_service import (
    AnalysisPersistenceService,
    DuplicateAnalysisError,
    PersistenceResult,
)
from src.database.sqlalchemy_manager import (
    SQLAlchemyDatabaseManager,
)

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
        if self.container.session_factory is not None:
            database_manager = SQLAlchemyDatabaseManager(
                self.container.session_factory
            )

            database_manager.create_schema()

            self.logger.info(
                "Database schema verified."
            )

    @property
    def settings(self) -> Settings:
        return self.container.settings

    @property
    def analysis_persistence_service(
        self,
    ) -> AnalysisPersistenceService | None:
        return self.container.analysis_persistence_service

    @property
    def database_enabled(self) -> bool:
        return (
            self.settings.database.enabled
            and self.analysis_persistence_service is not None
        )

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

    def save_analysis(
        self,
        telemetry_session: TelemetrySession,
        kpi_results: dict[str, list[KPI]],
        session_name: str | None = None,
        session_type: str = "other",
    ) -> PersistenceResult:
        if not self.database_enabled:
            raise RuntimeError(
                "Database persistence is disabled."
            )

        persistence_service = (
            self.analysis_persistence_service
        )

        if persistence_service is None:
            raise RuntimeError(
                "Analysis persistence service is unavailable."
            )

        self.logger.info(
            "Saving analysis: file=%s session_name=%s",
            telemetry_session.filename,
            session_name or telemetry_session.source_file.stem,
        )

        try:
            result = persistence_service.save_analysis(
                telemetry_session=telemetry_session,
                kpi_results=kpi_results,
                session_name=session_name,
                session_type=session_type,
            )

        except Exception:
            self.logger.exception(
                "Analysis persistence failed: %s",
                telemetry_session.filename,
            )
            raise

        self.logger.info(
            "Analysis saved: race_session_id=%s kpis=%s",
            result.race_session_id,
            result.kpi_count,
        )

        return result

    def shutdown(self) -> None:
        if self.container.session_factory is not None:
            self.container.session_factory.dispose()

            self.logger.info(
                "Database connection pool disposed."
            )

    def analysis_exists(
        self,
        telemetry_session: TelemetrySession,
    ) -> bool:
        persistence_service = (
            self.analysis_persistence_service
        )

        if persistence_service is None:
            return False

        return persistence_service.analysis_exists(
            telemetry_session
        )

    def existing_analysis_id(
        self,
        telemetry_session: TelemetrySession,
    ) -> int | None:
        persistence_service = (
            self.analysis_persistence_service
        )

        if persistence_service is None:
            return None

        return (
            persistence_service
            .find_existing_session_id(
                telemetry_session
            )
        )

    def recent_analyses(
        self,
        limit: int = 10,
    ) -> list[dict]:
        persistence_service = (
            self.analysis_persistence_service
        )

        if persistence_service is None:
            return []

        return persistence_service.recent_sessions(
            limit=limit
        )