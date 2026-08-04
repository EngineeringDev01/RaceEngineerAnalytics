from pathlib import Path

import pandas as pd

from src.core.telemetry_session import TelemetrySession
from src.importers.base import TelemetryImporter


class GenericCSVImporter(TelemetryImporter):
    source_system = "Generic CSV"

    def can_import(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".csv"

    def load(self, file_path: Path) -> TelemetrySession:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Telemetry file not found: {file_path}"
            )

        dataframe = pd.read_csv(
            file_path,
            sep=None,
            engine="python",
        )

        if dataframe.empty:
            raise ValueError(
                f"No data found in '{file_path.name}'."
            )

        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        return TelemetrySession(
            source_file=file_path,
            dataframe=dataframe,
            source_system=self.source_system,
        )