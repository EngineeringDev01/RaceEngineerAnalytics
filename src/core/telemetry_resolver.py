from __future__ import annotations

from typing import Any

import pandas as pd

from src.core.channels import CHANNEL_DEFINITIONS
from src.core.telemetry_session import TelemetrySession


class TelemetryResolver:
    """
    Central interface for accessing engineering telemetry signals.

    The resolver hides source-specific channel names from analysis and
    visualization modules. All downstream code works with canonical names
    such as ``speed``, ``throttle`` and ``brake_front``.

    Future responsibilities may include:

    - unit normalization;
    - derived channels;
    - signal filtering;
    - interpolation;
    - resampling;
    - signal quality validation.
    """

    def __init__(
        self,
        session: TelemetrySession,
    ) -> None:
        self.session = session

    def channel(
        self,
        canonical_name: str,
    ) -> pd.Series:
        """
        Return a telemetry channel using its canonical name.

        Raises
        ------
        KeyError
            If the canonical channel is unknown or unavailable.
        """
        return self.session.get_canonical_channel(
            canonical_name
        )

    def has_channel(
        self,
        canonical_name: str,
    ) -> bool:
        """Return whether a canonical channel is available."""
        return self.session.has_canonical_channel(
            canonical_name
        )

    def source_channel_name(
        self,
        canonical_name: str,
    ) -> str | None:
        """
        Return the original source-specific channel name.

        Examples
        --------
        ``speed`` may resolve to ``Wheel Speed FL`` in MoTeC or
        ``V_VEH`` in a Bosch export.
        """
        return self.session.resolve_channel(
            canonical_name
        )

    def available_channels(self) -> dict[str, str]:
        """
        Return all resolved canonical-to-source mappings.

        Example
        -------
        {
            "speed": "Wheel Speed FL",
            "throttle": "Throttle Pos",
        }
        """
        return self.session.resolved_channels()

    def display_name(
        self,
        canonical_name: str,
    ) -> str:
        """Return the user-facing engineering channel name."""
        definition = CHANNEL_DEFINITIONS.get(
            canonical_name
        )

        if definition is None:
            return canonical_name

        return definition.display_name

    def channel_unit(
        self,
        canonical_name: str,
    ) -> str | None:
        """
        Return the expected canonical engineering unit.

        The imported source unit is preferred when available. Otherwise,
        the unit declared in the canonical channel definition is returned.
        """
        source_channel = self.source_channel_name(
            canonical_name
        )

        if source_channel is not None:
            source_unit = self.session.units.get(
                source_channel
            )

            if source_unit:
                return source_unit

        definition = CHANNEL_DEFINITIONS.get(
            canonical_name
        )

        if definition is None:
            return None

        return definition.unit

    def channel_information(
        self,
        canonical_name: str,
    ) -> dict[str, Any]:
        """Return metadata about a resolved engineering channel."""
        source_name = self.source_channel_name(
            canonical_name
        )

        return {
            "canonical_name": canonical_name,
            "display_name": self.display_name(
                canonical_name
            ),
            "source_name": source_name,
            "unit": self.channel_unit(
                canonical_name
            ),
            "available": source_name is not None,
        }

    def time(self) -> pd.Series:
        return self.channel("time")

    def distance(self) -> pd.Series:
        return self.channel("distance")

    def speed(self) -> pd.Series:
        return self.channel("speed")

    def rpm(self) -> pd.Series:
        return self.channel("rpm")

    def throttle(self) -> pd.Series:
        return self.channel("throttle")

    def brake(self) -> pd.Series:
        """
        Return the best available general brake signal.

        Preference order:

        1. Generic brake channel
        2. Front brake pressure
        3. Rear brake pressure
        """
        for canonical_name in (
            "brake",
            "brake_front",
            "brake_rear",
        ):
            if self.has_channel(canonical_name):
                return self.channel(canonical_name)

        raise KeyError(
            "No brake channel is available in "
            f"'{self.session.filename}'."
        )

    def brake_front(self) -> pd.Series:
        return self.channel("brake_front")

    def brake_rear(self) -> pd.Series:
        return self.channel("brake_rear")

    def steering(self) -> pd.Series:
        return self.channel("steering")

    def gear(self) -> pd.Series:
        return self.channel("gear")

    def lateral_g(self) -> pd.Series:
        return self.channel("lateral_g")

    def longitudinal_g(self) -> pd.Series:
        return self.channel("longitudinal_g")

    def lap_number(self) -> pd.Series:
        return self.channel("lap_number")

    def lap_distance(self) -> pd.Series:
        return self.channel("lap_distance")

    def lap_time(self) -> pd.Series:
        return self.channel("lap_time")

    def summary(self) -> dict[str, Any]:
        """Return a summary of the resolved engineering data."""
        return {
            "filename": self.session.filename,
            "source_system": self.session.source_system,
            "samples": self.session.samples,
            "resolved_channels": self.available_channels(),
        }
    def track_x(self) -> pd.Series:
        return self.channel("track_x")

    def track_y(self) -> pd.Series:
        return self.channel("track_y")

    def track_z(self) -> pd.Series:
        return self.channel("track_z")

    def gps_latitude(self) -> pd.Series:
        return self.channel("gps_latitude")

    def gps_longitude(self) -> pd.Series:
        return self.channel("gps_longitude")
    def has_track_map(self) -> bool:
        has_cartesian_coordinates = (
            self.has_channel("track_x")
            and self.has_channel("track_y")
        )   

        has_geographic_coordinates = (
            self.has_channel("gps_latitude")
            and self.has_channel("gps_longitude")
        )

        return (
            has_cartesian_coordinates
            or has_geographic_coordinates
        )