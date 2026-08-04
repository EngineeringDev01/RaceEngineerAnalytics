from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.core.telemetry_resolver import TelemetryResolver
from src.core.telemetry_session import TelemetrySession
from src.domain.lap import Lap


@dataclass(frozen=True)
class LapDetectionResult:
    laps: list[Lap]
    method: str
    warnings: list[str]

    @property
    def lap_count(self) -> int:
        return len(self.laps)


class LapDetector:
    """
    Detect laps from an imported telemetry session.

    Detection priority
    ------------------
    1. Explicit lap-number channel.
    2. Resets in the lap-distance channel.
    3. Treat the complete file as one lap.
    """

    def __init__(
        self,
        session: TelemetrySession,
        minimum_samples_per_lap: int = 10,
        reset_threshold_m: float = 100.0,
    ) -> None:
        self.session = session
        self.resolver = TelemetryResolver(session)
        self.minimum_samples_per_lap = minimum_samples_per_lap
        self.reset_threshold_m = reset_threshold_m

    def detect(self) -> LapDetectionResult:
        warnings: list[str] = []

        if self.resolver.has_channel("lap_number"):
            laps = self._detect_from_lap_number()

            if laps:
                return LapDetectionResult(
                    laps=laps,
                    method="lap_number",
                    warnings=warnings,
                )

            warnings.append(
                "The lap-number channel was present but produced no valid laps."
            )

        if self.resolver.has_channel("lap_distance"):
            laps = self._detect_from_lap_distance()

            if laps:
                return LapDetectionResult(
                    laps=laps,
                    method="lap_distance_reset",
                    warnings=warnings,
                )

            warnings.append(
                "The lap-distance channel was present but no resets were detected."
            )

        warnings.append(
            "No multi-lap marker was found. The complete file was treated as one lap."
        )

        return LapDetectionResult(
            laps=[self._build_lap(1, 0, self.session.samples - 1)],
            method="whole_file",
            warnings=warnings,
        )

    def extract_lap_dataframe(
        self,
        lap: Lap,
    ) -> pd.DataFrame:
        if lap.telemetry_start_index is None:
            raise ValueError(
                f"Lap {lap.number} has no telemetry start index."
            )

        if lap.telemetry_end_index is None:
            raise ValueError(
                f"Lap {lap.number} has no telemetry end index."
            )

        dataframe = self.session.dataframe.iloc[
            lap.telemetry_start_index : lap.telemetry_end_index + 1
        ].copy()

        dataframe.reset_index(
            drop=True,
            inplace=True,
        )

        return dataframe

    def _detect_from_lap_number(self) -> list[Lap]:
        lap_numbers = pd.to_numeric(
            self.resolver.lap_number(),
            errors="coerce",
        )

        valid_mask = lap_numbers.notna()

        if not valid_mask.any():
            return []

        laps: list[Lap] = []

        valid_lap_numbers = (
            lap_numbers[valid_mask]
            .astype(int)
            .drop_duplicates()
            .tolist()
        )

        for lap_number in valid_lap_numbers:
            positions = np.flatnonzero(
                lap_numbers.to_numpy() == lap_number
            )

            if len(positions) < self.minimum_samples_per_lap:
                continue

            laps.append(
                self._build_lap(
                    number=lap_number,
                    start_index=int(positions[0]),
                    end_index=int(positions[-1]),
                )
            )

        return laps

    def _detect_from_lap_distance(self) -> list[Lap]:
        lap_distance = pd.to_numeric(
            self.resolver.lap_distance(),
            errors="coerce",
        )

        lap_distance = lap_distance.interpolate(
            limit_direction="both"
        )

        if lap_distance.empty:
            return []

        difference = lap_distance.diff()

        reset_positions = np.flatnonzero(
            difference.to_numpy() < -abs(self.reset_threshold_m)
        )

        boundaries = [0]

        boundaries.extend(
            int(position)
            for position in reset_positions
        )

        boundaries.append(len(lap_distance))

        boundaries = sorted(set(boundaries))

        laps: list[Lap] = []

        for boundary_index in range(len(boundaries) - 1):
            start_index = boundaries[boundary_index]
            end_exclusive = boundaries[boundary_index + 1]
            end_index = end_exclusive - 1

            sample_count = end_index - start_index + 1

            if sample_count < self.minimum_samples_per_lap:
                continue

            laps.append(
                self._build_lap(
                    number=len(laps) + 1,
                    start_index=start_index,
                    end_index=end_index,
                )
            )

        return laps

    def _build_lap(
        self,
        number: int,
        start_index: int,
        end_index: int,
    ) -> Lap:
        lap_time_s = self._calculate_lap_time(
            start_index,
            end_index,
        )

        return Lap(
            number=number,
            lap_time_s=lap_time_s,
            telemetry_start_index=start_index,
            telemetry_end_index=end_index,
        )

    def _calculate_lap_time(
        self,
        start_index: int,
        end_index: int,
    ) -> float | None:
        if self.resolver.has_channel("lap_time"):
            lap_time = pd.to_numeric(
                self.resolver.lap_time().iloc[
                    start_index : end_index + 1
                ],
                errors="coerce",
            ).dropna()

            if not lap_time.empty:
                return float(lap_time.max() - lap_time.min())

        if self.resolver.has_channel("time"):
            session_time = pd.to_numeric(
                self.resolver.time().iloc[
                    start_index : end_index + 1
                ],
                errors="coerce",
            ).dropna()

            if len(session_time) >= 2:
                return float(
                    session_time.iloc[-1] - session_time.iloc[0]
                )

        return None