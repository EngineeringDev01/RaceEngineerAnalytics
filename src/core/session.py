from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from src.core.channels import (
    CHANNEL_DEFINITIONS,
    find_matching_channel,
)


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
                f"Channel '{channel_name}' is not available "
                f"in '{self.filename}'."
            )

        return self.dataframe[channel_name]

    def resolve_channel(
        self,
        canonical_name: str,
    ) -> str | None:
        return find_matching_channel(
            self.dataframe.columns,
            canonical_name,
        )

    def has_canonical_channel(
        self,
        canonical_name: str,
    ) -> bool:
        return self.resolve_channel(canonical_name) is not None

    def get_canonical_channel(
        self,
        canonical_name: str,
    ) -> pd.Series:
        source_channel = self.resolve_channel(canonical_name)

        if source_channel is None:
            raise KeyError(
                f"Canonical channel '{canonical_name}' "
                f"is unavailable in '{self.filename}'."
            )

        return self.dataframe[source_channel]

    def resolved_channels(self) -> dict[str, str]:
        resolved: dict[str, str] = {}

        for canonical_name in CHANNEL_DEFINITIONS:
            source_channel = self.resolve_channel(canonical_name)

            if source_channel is not None:
                resolved[canonical_name] = source_channel

        return resolved

    def summary(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "source_system": self.source_system,
            "samples": self.samples,
            "channels": len(self.channels),
            "metadata": self.metadata,
            "resolved_channels": self.resolved_channels(),
        }