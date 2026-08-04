from collections.abc import Sequence

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.channels import CHANNEL_DEFINITIONS
from src.core.telemetry_session import TelemetrySession


class TelemetryPlotter:
    def __init__(
        self,
        session: TelemetrySession,
    ) -> None:
        self.session = session

    def available_canonical_channels(self) -> dict[str, str]:
        return self.session.resolved_channels()

    def create_channel_plot(
        self,
        x_channel: str,
        y_channels: Sequence[str],
        separate_axes: bool = True,
    ) -> go.Figure:
        if not y_channels:
            raise ValueError(
                "At least one Y-axis channel must be selected."
            )

        x_source_name = self.session.resolve_channel(x_channel)

        if x_source_name is None:
            raise KeyError(
                f"X-axis channel '{x_channel}' is unavailable."
            )

        x_data = self.session.get_canonical_channel(x_channel)

        if separate_axes:
            figure = self._create_separate_axis_plot(
                x_channel=x_channel,
                x_data=x_data,
                y_channels=y_channels,
            )
        else:
            figure = self._create_single_axis_plot(
                x_channel=x_channel,
                x_data=x_data,
                y_channels=y_channels,
            )


        figure.update_layout(
            title="Dynamic Telemetry Viewer",
            hovermode="x unified",
            height=max(500, 250 * len(y_channels)),
            margin=dict(
                l=70,
                r=40,
                t=70,
                b=60,
            ),
        )

        return figure

    def _create_separate_axis_plot(
        self,
        x_channel: str,
        x_data,
        y_channels: Sequence[str],
    ) -> go.Figure:
        figure = make_subplots(
            rows=len(y_channels),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
        )

        x_label = self._display_name(x_channel)
        x_unit = self._unit(x_channel)

        for row, canonical_name in enumerate(
            y_channels,
            start=1,
        ):
            source_name = self.session.resolve_channel(
                canonical_name
            )

            if source_name is None:
                continue

            y_data = self.session.get_canonical_channel(
                canonical_name
            )

            label = self._display_name(canonical_name)
            unit = self._unit(canonical_name)

            figure.add_trace(
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    name=label,
                    mode="lines",
                    customdata=[source_name] * len(y_data),
                    hovertemplate=(
                        f"{label}: %{{y:.3f}}"
                        f"{f' {unit}' if unit else ''}"
                        "<br>"
                        f"{x_label}: %{{x:.3f}}"
                        f"{f' {x_unit}' if x_unit else ''}"
                        "<br>"
                        f"Source: {source_name}"
                        "<extra></extra>"
                    ),
                ),
                row=row,
                col=1,
            )

            figure.update_yaxes(
                title_text=(
                    f"{label}"
                    f"{f' [{unit}]' if unit else ''}"
                ),
                row=row,
                col=1,
            )

        figure.update_xaxes(
            title_text=(
                f"{x_label}"
                f"{f' [{x_unit}]' if x_unit else ''}"
            ),
            row=len(y_channels),
            col=1,
        )

        return figure

    def _create_single_axis_plot(
        self,
        x_channel: str,
        x_data,
        y_channels: Sequence[str],
    ) -> go.Figure:
        figure = go.Figure()

        x_label = self._display_name(x_channel)
        x_unit = self._unit(x_channel)

        for canonical_name in y_channels:
            source_name = self.session.resolve_channel(
                canonical_name
            )

            if source_name is None:
                continue

            y_data = self.session.get_canonical_channel(
                canonical_name
            )

            label = self._display_name(canonical_name)
            unit = self._unit(canonical_name)

            figure.add_trace(
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    name=label,
                    mode="lines",
                    hovertemplate=(
                        f"{label}: %{{y:.3f}}"
                        f"{f' {unit}' if unit else ''}"
                        "<br>"
                        f"{x_label}: %{{x:.3f}}"
                        f"{f' {x_unit}' if x_unit else ''}"
                        "<br>"
                        f"Source: {source_name}"
                        "<extra></extra>"
                    ),
                )
            )

        figure.update_xaxes(
            title_text=(
                f"{x_label}"
                f"{f' [{x_unit}]' if x_unit else ''}"
            )
        )

        figure.update_yaxes(
            title_text="Selected channels"
        )

        return figure

    @staticmethod
    def _display_name(
        canonical_name: str,
    ) -> str:
        definition = CHANNEL_DEFINITIONS.get(
            canonical_name
        )

        if definition is None:
            return canonical_name

        return definition.display_name

    @staticmethod
    def _unit(
        canonical_name: str,
    ) -> str | None:
        definition = CHANNEL_DEFINITIONS.get(
            canonical_name
        )

        if definition is None:
            return None

        return definition.unit