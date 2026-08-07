from __future__ import annotations

from dataclasses import dataclass, field

from src.importers.factory import ImporterFactory
from src.services.kpi_export_service import KPIExportService
from src.services.telemetry_service import TelemetryService


@dataclass
class ServiceContainer:
    """
    Application dependency container.

    The container owns shared services and their dependencies.
    User interfaces such as Streamlit, CLI, REST API, or future desktop
    applications should obtain services from this object instead of
    creating them directly.
    """

    importer_factory: ImporterFactory = field(
        default_factory=ImporterFactory
    )

    telemetry_service: TelemetryService = field(
        init=False
    )

    kpi_export_service: KPIExportService = field(
        default_factory=KPIExportService
    )

    def __post_init__(self) -> None:
        self.telemetry_service = TelemetryService(
            importer_factory=self.importer_factory
        )