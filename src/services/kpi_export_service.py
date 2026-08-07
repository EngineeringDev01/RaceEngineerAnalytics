from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.core.kpi import KPI


class KPIExportService:
    """
    Convert engineering KPI results into reusable export formats.

    Supported outputs:
    - pandas DataFrame
    - CSV
    - JSON

    Future outputs:
    - SQLAlchemy / MySQL
    - API payloads
    - report generators
    """

    @staticmethod
    def flatten(
        kpi_results: dict[str, list[KPI]],
    ) -> list[KPI]:
        """
        Flatten KPI categories into a single KPI list.
        """
        flattened: list[KPI] = []

        for kpis in kpi_results.values():
            flattened.extend(kpis)

        return flattened

    @classmethod
    def to_records(
        cls,
        kpi_results: dict[str, list[KPI]],
    ) -> list[dict[str, Any]]:
        """
        Convert KPI results into serializable dictionary records.
        """
        return [
            kpi.to_dict()
            for kpi in cls.flatten(kpi_results)
        ]

    @classmethod
    def to_dataframe(
        cls,
        kpi_results: dict[str, list[KPI]],
    ) -> pd.DataFrame:
        """
        Convert KPI results into a pandas DataFrame.
        """
        records = cls.to_records(kpi_results)

        columns = [
            "category",
            "name",
            "value",
            "unit",
            "source_channel",
            "description",
        ]

        if not records:
            return pd.DataFrame(
                columns=columns
            )

        dataframe = pd.DataFrame(records)

        return dataframe[
            columns
        ]

    @classmethod
    def to_csv(
        cls,
        kpi_results: dict[str, list[KPI]],
        file_path: str | Path,
    ) -> Path:
        """
        Export KPI results to CSV.
        """
        output_path = Path(file_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe = cls.to_dataframe(
            kpi_results
        )

        dataframe.to_csv(
            output_path,
            index=False,
        )

        return output_path

    @classmethod
    def to_json(
        cls,
        kpi_results: dict[str, list[KPI]],
        file_path: str | Path,
    ) -> Path:
        """
        Export KPI results to JSON.
        """
        output_path = Path(file_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        records = cls.to_records(
            kpi_results
        )

        output_path.write_text(
            json.dumps(
                records,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return output_path