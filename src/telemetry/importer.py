from pathlib import Path
import pandas as pd

from .session import TelemetrySession


class TelemetryImporter:

    @staticmethod
    def load_motec_csv(file_path: str):

        path = Path(file_path)

        # Find the channel header row
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        header_row = None

        for index, line in enumerate(lines):
            if line.startswith('"Time"'):
                header_row = index
                break

        if header_row is None:
            raise ValueError(
                "MoTeC channel header not found"
            )

        print(f"Detected telemetry header at row {header_row}")

        # Load telemetry data
        df = pd.read_csv(
            path,
            skiprows=header_row,
            header=0
        )

        # Remove units row
        df = df.iloc[1:]

        # Convert columns to numeric
        df = df.apply(
            pd.to_numeric,
            errors="coerce"
        )

        # Remove empty columns
        df.dropna(
            axis=1,
            how="all",
            inplace=True
        )

        return TelemetrySession(
            filename=path.name,
            dataframe=df
        )