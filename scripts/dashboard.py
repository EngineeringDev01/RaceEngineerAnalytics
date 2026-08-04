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
    factory = ImporterFactory()

    session = factory.load(
        temporary_file
    )

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


st.subheader(
    "Speed, Throttle and Brake"
)


try:
    plotter = TelemetryPlotter(
        session.dataframe
    )

    figure = (
        plotter.speed_throttle_brake()
    )

    st.plotly_chart(
        figure,
        width="stretch",
    )

except KeyError as error:
    st.warning(
        "The file was imported successfully, "
        "but the standard Speed/Throttle/Brake "
        f"view could not be generated: {error}"
    )

except Exception as error:
    st.error(
        "The telemetry chart could not be generated."
    )

    st.exception(error)