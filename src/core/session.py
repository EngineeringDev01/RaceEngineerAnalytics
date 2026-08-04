from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class TelemetrySession:
    source_file: Path
    dataframe: pd.DataFrame
    source_system: str
    metadata: dict[str, Any] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)

    @property
    def filename(self) -> str:
        return self.source_file.name

    @property
    def channels(self) -> list[str]:
        return list(self.dataframe.columns)

    @property
    def samples(self) -> int:
        return len(self.dataframe)

    def has_channel(self, channel_name: str) -> bool:
        return channel_name in self.dataframe.columns

    def get_channel(self, channel_name: str) -> pd.Series:
        if not self.has_channel(channel_name):
            raise KeyError(
                f"Channel '{channel_name}' is not available in "
                f"'{self.filename}'."
            )

        return self.dataframe[channel_name]

    def summary(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "source_system": self.source_system,
            "samples": self.samples,
            "channels": len(self.channels),
            "metadata": self.metadata,
        }