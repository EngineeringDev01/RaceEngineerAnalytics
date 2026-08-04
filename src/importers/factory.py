from pathlib import Path

from src.core.session import TelemetrySession
from src.importers.base import TelemetryImporter
from src.importers.generic_csv import GenericCSVImporter
from src.importers.motec import MoTeCCSVImporter


class ImporterFactory:
    def __init__(self) -> None:
        self.importers: list[TelemetryImporter] = [
            MoTeCCSVImporter(),
            GenericCSVImporter(),
        ]

    def load(self, file_path: str | Path) -> TelemetrySession:
        path = Path(file_path)

        for importer in self.importers:
            if importer.can_import(path):
                return importer.load(path)

        supported_extensions = sorted(
            {
                extension
                for extension in [".csv"]
            }
        )

        raise ValueError(
            f"No importer supports '{path.name}'. "
            f"Currently supported: {', '.join(supported_extensions)}."
        )