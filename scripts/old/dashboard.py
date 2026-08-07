import sys
import tempfile
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.services.telemetry_service import TelemetryService
from src.visualization.plots import TelemetryPlotter
from src.analysis.lap_detector import LapDetector
from src.core.telemetry_resolver import TelemetryResolver
from src.visualization.track_map import TrackMapPlotter

st.set_page_config(
    page_title="Race Engineer Analytics",
    page_icon="🏎️",
    layout="wide",
)


st.title("🏎️ Race Engineer Analytics")

st.write(
    "Upload a telemetry CSV export. "
    "MoTeC CSV and standard CSV files are currently supported."
)


uploaded_file = st.file_uploader(
    "Select telemetry file",
    type=["csv"],
)


if uploaded_file is None:
    st.info("Select a CSV telemetry file to start the analysis.")
    st.stop()


temporary_directory = (
    Path(tempfile.gettempdir())
    / "race_engineer_analytics"
)

temporary_directory.mkdir(
    parents=True,
    exist_ok=True,
)


temporary_file = (
    temporary_directory
    / uploaded_file.name
)

temporary_file.write_bytes(
    uploaded_file.getbuffer()
)


try:
    telemetry_service = TelemetryService()
    session = telemetry_service.load(temporary_file)

except Exception as error:
    st.error(
        "The telemetry file could not be imported."
    )

    st.exception(error)
    st.stop()


st.subheader("Session Summary")


file_column, source_column, samples_column, channels_column = (
    st.columns(4)
)


file_column.metric(
    label="File",
    value=session.filename,
)

source_column.metric(
    label="Source",
    value=session.source_system,
)

samples_column.metric(
    label="Samples",
    value=f"{session.samples:,}",
)

channels_column.metric(
    label="Channels",
    value=len(session.channels),
)


if session.metadata:
    st.subheader("Session Metadata")

    metadata_columns = st.columns(4)

    metadata_columns[0].metric(
        label="Vehicle",
        value=session.metadata.get(
            "Vehicle",
            "Unknown",
        ),
    )

    metadata_columns[1].metric(
        label="Driver",
        value=session.metadata.get(
            "Driver",
            "Unknown",
        ),
    )

    metadata_columns[2].metric(
        label="Venue",
        value=session.metadata.get(
            "Venue",
            "Unknown",
        ),
    )

    metadata_columns[3].metric(
        label="Duration",
        value=session.metadata.get(
            "Duration",
            "Unknown",
        ),
    )


with st.expander(
    "Available telemetry channels"
):
    channel_rows = []

    for channel in session.channels:
        channel_rows.append(
            {
                "Channel": channel,
                "Unit": session.units.get(
                    channel,
                    "",
                ),
            }
        )

    st.dataframe(
        channel_rows,
        width="stretch",
        hide_index=True,
    )


st.subheader("Dynamic Telemetry Viewer")

plotter = TelemetryPlotter(session)
resolver = TelemetryResolver(session)

resolved_channels = (
    plotter.available_canonical_channels()
)

if not resolved_channels:
    st.warning(
        "No canonical engineering channels "
        "could be resolved in this file."
    )
    st.stop()


channel_labels = {}

for canonical_name, source_name in resolved_channels.items():
    display_name = plotter.resolver.display_name(
        canonical_name
    )

    unit = plotter.resolver.channel_unit(
        canonical_name
    )

    unit_text = f" [{unit}]" if unit else ""

    channel_labels[canonical_name] = (
        f"{display_name}{unit_text} ← {source_name}"
    )

possible_x_channels = [
    channel
    for channel in (
        "distance",
        "time",
    )
    if channel in resolved_channels
]


if not possible_x_channels:
    st.warning(
        "Neither Distance nor Time is available "
        "for the X axis."
    )
    st.stop()


default_x_index = 0

x_channel = st.selectbox(
    "X axis",
    options=possible_x_channels,
    index=default_x_index,
    format_func=lambda value: channel_labels[value],
)


selectable_y_channels = [
    channel
    for channel in resolved_channels
    if channel != x_channel
]


default_y_channels = [
    channel
    for channel in (
        "speed",
        "throttle",
        "brake_front",
    )
    if channel in selectable_y_channels
]


selected_y_channels = st.multiselect(
    "Telemetry channels",
    options=selectable_y_channels,
    default=default_y_channels,
    format_func=lambda value: channel_labels[value],
)


separate_axes = st.checkbox(
    "Display channels on separate synchronized plots",
    value=True,
)


if not selected_y_channels:
    st.info(
        "Select at least one telemetry channel."
    )
    st.stop()

try:
    figure = plotter.create_channel_plot(
        x_channel=x_channel,
        y_channels=selected_y_channels,
        separate_axes=separate_axes,
    )

    st.plotly_chart(
        figure,
        width="stretch",
    )

except KeyError as error:
    st.warning(
        "A required telemetry channel could not be resolved: "
        f"{error}"
    )

except ValueError as error:
    st.warning(str(error))

except Exception as error:
    st.error(
        "The dynamic telemetry plot could not be generated."
    )
    st.exception(error)
st.divider()
st.subheader("Lap Detection and Comparison")

lap_detector = LapDetector(session)
lap_result = lap_detector.detect()

lap_column, method_column = st.columns(2)

lap_column.metric(
    "Detected Laps",
    lap_result.lap_count,
)

method_column.metric(
    "Detection Method",
    lap_result.method,
)

for warning in lap_result.warnings:
    st.warning(warning)


lap_rows = [
    {
        "Lap": lap.number,
        "Lap Time [s]": (
            round(lap.lap_time_s, 3)
            if lap.lap_time_s is not None
            else None
        ),
        "Start Sample": lap.telemetry_start_index,
        "End Sample": lap.telemetry_end_index,
        "Samples": (
            lap.telemetry_end_index
            - lap.telemetry_start_index
            + 1
            if lap.telemetry_start_index is not None
            and lap.telemetry_end_index is not None
            else None
        ),
    }
    for lap in lap_result.laps
]

st.dataframe(
    lap_rows,
    width="stretch",
    hide_index=True,
)


if lap_result.lap_count < 2:
    st.info(
        "This file contains fewer than two detected laps. "
        "Upload a full multi-lap session to enable lap comparison."
    )

else:
    lap_options = {
        lap.number: lap
        for lap in lap_result.laps
    }

    selected_lap_numbers = st.multiselect(
        "Laps to compare",
        options=list(lap_options),
        default=list(lap_options)[:2],
        format_func=lambda value: f"Lap {value}",
    )

    comparison_channels = [
        channel
        for channel in (
            "speed",
            "throttle",
            "brake_front",
            "brake",
            "steering",
            "rpm",
            "gear",
        )
        if channel in resolved_channels
    ]

    default_comparison_channels = [
        channel
        for channel in (
            "speed",
            "throttle",
            "brake_front",
        )
        if channel in comparison_channels
    ]

    selected_comparison_channels = st.multiselect(
        "Lap comparison channels",
        options=comparison_channels,
        default=default_comparison_channels,
        format_func=lambda value: channel_labels[value],
    )

    if len(selected_lap_numbers) < 2:
        st.info("Select at least two laps.")

    elif not selected_comparison_channels:
        st.info(
            "Select at least one lap-comparison channel."
        )

    else:
        selected_laps = [
            lap_options[number]
            for number in selected_lap_numbers
        ]

        try:
            comparison_figure = (
                plotter.create_lap_comparison_plot(
                    laps=selected_laps,
                    channels=selected_comparison_channels,
                )
            )

            st.plotly_chart(
                comparison_figure,
                width="stretch",
            )

        except Exception as error:
            st.error(
                "The selected laps could not be compared."
            )
            st.exception(error)