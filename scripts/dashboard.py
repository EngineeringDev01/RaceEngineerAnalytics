import sys
import tempfile
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.importers.factory import ImporterFactory
from src.visualization.plots import TelemetryPlotter


st.set_page_config(
    page_title="Race Engineer Analytics",
    page_icon="🏎️",
    layout="wide",
)

st.title("🏎️ Race Engineer Analytics")

uploaded_file = st.file_uploader(
    "Select a telemetry export",
    type=["csv"],
    help=(
        "The original filename is retained. "
        "MoTeC CSV and standard CSV files are currently supported."
    ),
)

if uploaded_file is None:
    st.info("Select a telemetry file to begin the analysis.")
    st.stop()


temporary_directory = Path(tempfile.gettempdir()) / "race_engineer_analytics"
temporary_directory.mkdir(
    parents=True,
    exist_ok=True,
)

temporary_file = temporary_directory / uploaded_file.name
temporary_file.write_bytes(uploaded_file.getbuffer())


try:
    importer_factory = ImporterFactory()
    session = importer_factory.load(temporary_file)

except Exception as error:
    st.error("The telemetry file could not be imported.")
    st.exception(error)
    st.stop()


st.subheader("Session Summary")

file_column, system_column, samples_column, channels_column = st.columns(4)

file_column.metric(
    "File",
    session.filename,
)

system_column.metric(
    "Source",
    session.source_system,
)

samples_column.metric(
    "Samples",
    f"{session.samples:,}",
)

channels_column.metric(
    "Channels",
    len(session.channels),
)


metadata = session.metadata

if metadata:
    metadata_columns = st.columns(4)

    metadata_columns[0].metric(
        "Vehicle",
        metadata.get("Vehicle", "Unknown"),
    )

    metadata_columns[1].metric(
        "Driver",
        metadata.get("Driver", "Unknown"),
    )

    metadata_columns[2].metric(
        "Venue",
        metadata.get("Venue", "Unknown"),
    )

    metadata_columns[3].metric(
        "Duration",
        metadata.get("Duration", "Unknown"),
    )


with st.expander("Available telemetry channels"):
    st.dataframe(
        {
            "Channel": session.channels,
            "Unit": [
                session.units.get(channel, "")
                for channel in session.channels
            ],
        },
        width="stretch",
        hide_index=True,
    )


st.subheader("Speed, Throttle and Brake")

try:
    plotter = TelemetryPlotter(session.dataframe)
    figure = plotter.speed_throttle_brake()

    st.plotly_chart(
        figure,
        width="stretch",
    )

except KeyError as error:
    st.warning(
        "The file was imported successfully, but the standard "
        f"Speed/Throttle/Brake view cannot be generated: {error}"
    )

except Exception as error:
    st.error("The telemetry chart could not be generated.")
    st.exception(error)