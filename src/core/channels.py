from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ChannelDefinition:
    canonical_name: str
    display_name: str
    unit: str | None = None
    aliases: tuple[str, ...] = field(default_factory=tuple)


CHANNEL_DEFINITIONS: dict[str, ChannelDefinition] = {
    "time": ChannelDefinition(
        canonical_name="time",
        display_name="Time",
        unit="s",
        aliases=(
            "Time",
            "Session Time",
            "Elapsed Time",
            "TIME",
            "t",
        ),
    ),
    "distance": ChannelDefinition(
        canonical_name="distance",
        display_name="Distance",
        unit="m",
        aliases=(
            "Distance",
            "Lap Distance",
            "Distance Traveled",
            "DISTANCE",
            "sLap",
        ),
    ),
    "speed": ChannelDefinition(
        canonical_name="speed",
        display_name="Vehicle Speed",
        unit="km/h",
        aliases=(
            "Speed",
            "Vehicle Speed",
            "Wheel Speed FL",
            "Speed FL",
            "V_VEH",
            "vCar",
            "Car Speed",
        ),
    ),
    "rpm": ChannelDefinition(
        canonical_name="rpm",
        display_name="Engine RPM",
        unit="rpm",
        aliases=(
            "Engine RPM",
            "RPM",
            "N_ENG",
            "Engine Speed",
            "nEngine",
        ),
    ),
    "throttle": ChannelDefinition(
        canonical_name="throttle",
        display_name="Throttle Position",
        unit="%",
        aliases=(
            "Throttle Pos",
            "Throttle",
            "Throttle Position",
            "TPS",
            "THROTTLE",
            "APP",
        ),
    ),
    "brake_front": ChannelDefinition(
        canonical_name="brake_front",
        display_name="Front Brake Pressure",
        unit="bar",
        aliases=(
            "Brk_Press_Fnt",
            "Front Brake Pressure",
            "Brake Pressure Front",
            "P_BRAKE_F",
            "Brake_F",
        ),
    ),
    "brake_rear": ChannelDefinition(
        canonical_name="brake_rear",
        display_name="Rear Brake Pressure",
        unit="bar",
        aliases=(
            "Brk_Press_Rear",
            "Rear Brake Pressure",
            "Brake Pressure Rear",
            "P_BRAKE_R",
            "Brake_R",
        ),
    ),
    "brake": ChannelDefinition(
        canonical_name="brake",
        display_name="Brake Pressure",
        unit="bar",
        aliases=(
            "Brake",
            "Brake Pressure",
            "P_BRAKE",
            "BrakePress",
        ),
    ),
    "steering": ChannelDefinition(
        canonical_name="steering",
        display_name="Steering Angle",
        unit="deg",
        aliases=(
            "Steered Angle",
            "Steering Angle",
            "Steer Angle",
            "STEER_ANGLE",
            "SW Angle",
        ),
    ),
    "lateral_g": ChannelDefinition(
        canonical_name="lateral_g",
        display_name="Lateral Acceleration",
        unit="g",
        aliases=(
            "G Force Lat",
            "Lateral G",
            "Lat Acc",
            "AY",
            "aY",
        ),
    ),
    "longitudinal_g": ChannelDefinition(
        canonical_name="longitudinal_g",
        display_name="Longitudinal Acceleration",
        unit="g",
        aliases=(
            "G Force Long",
            "Longitudinal G",
            "Long Acc",
            "AX",
            "aX",
        ),
    ),
    "gear": ChannelDefinition(
        canonical_name="gear",
        display_name="Gear",
        aliases=(
            "Gear",
            "GEAR",
            "Current Gear",
            "Gear Number",
        ),
    ),
    "lap_number": ChannelDefinition(
        canonical_name="lap_number",
        display_name="Lap Number",
        aliases=(
            "Lap",
            "Lap Number",
            "Lap No",
            "LapNumber",
            "LAP",
            "nLap",
        ),
    ),
    "lap_distance": ChannelDefinition(
        canonical_name="lap_distance",
        display_name="Lap Distance",
        unit="m",
        aliases=(
            "Lap Distance",
            "LapDistance",
            "Distance Lap",
            "Dist Lap",
            "sLap",
        ),
    ),
    "lap_time": ChannelDefinition(
        canonical_name="lap_time",
        display_name="Lap Time",
        unit="s",
        aliases=(
            "Lap Time",
            "LapTime",
            "Current Lap Time",
            "Time Lap",
            "tLap",
        ),
    ),
    "track_x": ChannelDefinition(
        canonical_name="track_x",
        display_name="Track X Position",
        unit="m",
        aliases=(
            "X Circ Pos",
            "Track X",
            "X Position",
            "GPS X",
            "GPS_X",
            "Pos X",
            "Position X",
            "xCar",
        ),
    ),
    "track_y": ChannelDefinition(
        canonical_name="track_y",
        display_name="Track Y Position",
        unit="m",
        aliases=(
            "Y Circ Pos",
            "Track Y",
            "Y Position",
            "GPS Y",
            "GPS_Y",
            "Pos Y",
            "Position Y",
            "yCar",
        ),
    ),
    "track_z": ChannelDefinition(
        canonical_name="track_z",
        display_name="Track Z Position",
        unit="m",
        aliases=(
            "Z Circ Pos",
            "Track Z",
            "Z Position",
            "GPS Z",
            "GPS_Z",
            "Pos Z",
            "Position Z",
            "zCar",
        ),
    ),
    "gps_latitude": ChannelDefinition(
        canonical_name="gps_latitude",
        display_name="GPS Latitude",
        unit="deg",
        aliases=(
            "GPS Latitude",
            "Latitude",
            "GPS Lat",
            "Lat GPS",
        ),
    ),
    "gps_longitude": ChannelDefinition(
        canonical_name="gps_longitude",
        display_name="GPS Longitude",
        unit="deg",
        aliases=(
            "GPS Longitude",
            "Longitude",
            "GPS Lon",
            "GPS Long",
            "Lon GPS",
        ),
    ),
}


def normalize_channel_name(name: str) -> str:
    return "".join(
        character.lower()
        for character in name.strip()
        if character.isalnum()
    )


def find_matching_channel(
    columns: Iterable[str],
    canonical_name: str,
) -> str | None:
    definition = CHANNEL_DEFINITIONS.get(canonical_name)

    if definition is None:
        raise KeyError(
            f"Unknown canonical channel: '{canonical_name}'."
        )

    normalized_columns = {
        normalize_channel_name(column): column
        for column in columns
    }

    candidates = (
        definition.display_name,
        *definition.aliases,
    )

    for candidate in candidates:
        normalized_candidate = normalize_channel_name(candidate)

        if normalized_candidate in normalized_columns:
            return normalized_columns[normalized_candidate]

    return None


def get_channel_series(
    dataframe: pd.DataFrame,
    canonical_name: str,
) -> pd.Series:
    source_channel = find_matching_channel(
        dataframe.columns,
        canonical_name,
    )

    if source_channel is None:
        raise KeyError(
            f"No source channel found for canonical channel "
            f"'{canonical_name}'."
        )

    return dataframe[source_channel]