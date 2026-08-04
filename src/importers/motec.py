import csv
from pathlib import Path
from typing import Any

import pandas as pd

from src.core.session import TelemetrySession
from src.importers.base import TelemetryImporter


class MoTeCCSVImporter(TelemetryImporter):
    source_system = "MoTeC"

    def can_import(self, file_path: Path) -> bool:
        if file_path.suffix.lower() != ".csv":
            return False

        try:
            with file_path.open(
                "r",
                encoding="utf-8-sig",
                errors="replace",
            ) as file:
                first_line = file.readline()

            return "MoTeC CSV File" in first_line

        except OSError:
            return False

    def load(self, file_path: Path) -> TelemetrySession:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Telemetry file not found: {file_path}"
            )

        lines = file_path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()

        header_row = self._find_header_row(lines)
        metadata = self._parse_metadata(lines[:header_row])

        dataframe = pd.read_csv(
            file_path,
            skiprows=header_row,
            header=0,
        )

        if dataframe.empty:
            raise ValueError(
                f"No telemetry data found in '{file_path.name}'."
            )

        units = self._extract_units(dataframe)

        # The first dataframe row contains units, not samples.
        dataframe = dataframe.iloc[1:].copy()

        # Convert telemetry values to numeric when possible.
        dataframe = dataframe.apply(
            pd.to_numeric,
            errors="coerce",
        )

        dataframe.dropna(
            axis=1,
            how="all",
            inplace=True,
        )

        dataframe.reset_index(
            drop=True,
            inplace=True,
        )

        return TelemetrySession(
            source_file=file_path,
            dataframe=dataframe,
            source_system=self.source_system,
            metadata=metadata,
            units=units,
        )

    @staticmethod
    def _find_header_row(lines: list[str]) -> int:
        for index, line in enumerate(lines):
            stripped = line.lstrip("\ufeff").strip()

            if stripped.startswith('Time,') or stripped.startswith('"Time"'):
                return index

        raise ValueError(
            "The MoTeC telemetry channel header could not be found."
        )

    @staticmethod
    def _parse_metadata(lines: list[str]) -> dict[str, Any]:
        metadata: dict[str, Any] = {}

        for line in lines:
            if not line.strip():
                continue

            try:
                row = next(csv.reader([line]))
            except csv.Error:
                continue

            if len(row) < 2:
                continue

            key = row[0].strip()
            value = row[1].strip()

            if key:
                metadata[key] = value

        return metadata

    @staticmethod
    def _extract_units(
        dataframe: pd.DataFrame,
    ) -> dict[str, str]:
        if dataframe.empty:
            return {}

        units_row = dataframe.iloc[0]

        return {
            str(channel): str(unit).strip()
            for channel, unit in units_row.items()
            if pd.notna(unit) and str(unit).strip()
        }