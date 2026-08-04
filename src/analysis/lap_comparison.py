from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from src.analysis.lap_detector import LapDetector
from src.core.telemetry_resolver import TelemetryResolver
from src.core.telemetry_session import TelemetrySession
from src.domain.lap import Lap


class LapComparison:
    """
    Prepare multiple laps on a common lap-distance axis.

    Each channel is interpolated to the same distance grid so laps
    with different sample counts can be compared directly.
    """

    def __init__(
        self,
        session: TelemetrySession,
        detector: LapDetector | None = None,
    ) -> None:
        self.session = session
        self.resolver = TelemetryResolver(session)
        self.detector = detector or LapDetector(session)

    def prepare(
        self,
        laps: Sequence[Lap],
        channels: Sequence[str],
        points: int = 1000,
    ) -> dict[int, pd.DataFrame]:
        if len(laps) < 2:
            raise ValueError(
                "At least two laps are required for comparison."
            )

        if not channels:
            raise ValueError(
                "At least one comparison channel must be selected."
            )

        if points < 100:
            raise ValueError(
                "The interpolation grid must contain at least 100 points."
            )

        prepared_laps: dict[int, pd.DataFrame] = {}

        maximum_common_distance = self._common_maximum_distance(
            laps
        )

        distance_grid = np.linspace(
            0.0,
            maximum_common_distance,
            points,
        )

        for lap in laps:
            lap_dataframe = self.detector.extract_lap_dataframe(
                lap
            )

            prepared_laps[lap.number] = self._prepare_single_lap(
                lap_dataframe=lap_dataframe,
                channels=channels,
                distance_grid=distance_grid,
            )

        return prepared_laps

    def _common_maximum_distance(
        self,
        laps: Sequence[Lap],
    ) -> float:
        maximum_distances: list[float] = []

        distance_source = self.session.resolve_channel(
            "lap_distance"
        )

        if distance_source is None:
            distance_source = self.session.resolve_channel(
                "distance"
            )

        if distance_source is None:
            raise KeyError(
                "Lap comparison requires Lap Distance or Distance."
            )

        for lap in laps:
            dataframe = self.detector.extract_lap_dataframe(
                lap
            )

            distance = pd.to_numeric(
                dataframe[distance_source],
                errors="coerce",
            ).dropna()

            if distance.empty:
                continue

            normalized_distance = distance - distance.iloc[0]

            maximum_distances.append(
                float(normalized_distance.max())
            )

        if not maximum_distances:
            raise ValueError(
                "No valid distance data was found in the selected laps."
            )

        return min(maximum_distances)

    def _prepare_single_lap(
        self,
        lap_dataframe: pd.DataFrame,
        channels: Sequence[str],
        distance_grid: np.ndarray,
    ) -> pd.DataFrame:
        distance_source = self.session.resolve_channel(
            "lap_distance"
        )

        if distance_source is None:
            distance_source = self.session.resolve_channel(
                "distance"
            )

        if distance_source is None:
            raise KeyError(
                "Lap comparison requires a distance channel."
            )

        distance = pd.to_numeric(
            lap_dataframe[distance_source],
            errors="coerce",
        )

        distance = distance - distance.iloc[0]

        output = pd.DataFrame(
            {
                "lap_distance": distance_grid,
            }
        )

        for canonical_name in channels:
            source_channel = self.session.resolve_channel(
                canonical_name
            )

            if source_channel is None:
                raise KeyError(
                    f"Channel '{canonical_name}' is unavailable."
                )

            values = pd.to_numeric(
                lap_dataframe[source_channel],
                errors="coerce",
            )

            valid_mask = (
                distance.notna()
                & values.notna()
            )

            valid_distance = distance[valid_mask].to_numpy()
            valid_values = values[valid_mask].to_numpy()

            if len(valid_distance) < 2:
                output[canonical_name] = np.nan
                continue

            unique_distance, unique_indexes = np.unique(
                valid_distance,
                return_index=True,
            )

            unique_values = valid_values[unique_indexes]

            output[canonical_name] = np.interp(
                distance_grid,
                unique_distance,
                unique_values,
            )

        return output