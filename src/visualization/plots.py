from collections.abc import Sequence

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.telemetry_resolver import TelemetryResolver
from src.core.telemetry_session import TelemetrySession
from src.analysis.lap_comparison import LapComparison
from src.domain.lap import Lap

class TelemetryPlotter:
    """Create interactive telemetry plots from canonical channels."""

    def __init__(
        self,
        session: TelemetrySession,
    ) -> None:
        self.session = session
        self.resolver = TelemetryResolver(session)

    def available_canonical_channels(
        self,
    ) -> dict[str, str]:
        return self.resolver.available_channels()

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

        if not self.resolver.has_channel(x_channel):
            raise KeyError(
                f"X-axis channel '{x_channel}' is unavailable."
            )

        unavailable_channels = [
            channel
            for channel in y_channels
            if not self.resolver.has_channel(channel)
        ]

        if unavailable_channels:
            raise KeyError(
                "Unavailable Y-axis channels: "
                + ", ".join(unavailable_channels)
            )

        x_data = self.resolver.channel(x_channel)

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
            height=max(
                500,
                250 * len(y_channels),
            ),
            margin=dict(
                l=70,
                r=40,
                t=70,
                b=60,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="left",
                x=0,
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

        x_label = self.resolver.display_name(
            x_channel
        )
        x_unit = self.resolver.channel_unit(
            x_channel
        )

        for row, canonical_name in enumerate(
            y_channels,
            start=1,
        ):
            y_data = self.resolver.channel(
                canonical_name
            )

            source_name = (
                self.resolver.source_channel_name(
                    canonical_name
                )
            )

            display_name = self.resolver.display_name(
                canonical_name
            )

            unit = self.resolver.channel_unit(
                canonical_name
            )

            figure.add_trace(
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    name=display_name,
                    mode="lines",
                    hovertemplate=self._hover_template(
                        x_label=x_label,
                        x_unit=x_unit,
                        y_label=display_name,
                        y_unit=unit,
                        source_name=source_name,
                    ),
                ),
                row=row,
                col=1,
            )

            figure.update_yaxes(
                title_text=self._axis_title(
                    display_name,
                    unit,
                ),
                row=row,
                col=1,
            )

        figure.update_xaxes(
            title_text=self._axis_title(
                x_label,
                x_unit,
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

        x_label = self.resolver.display_name(
            x_channel
        )

        x_unit = self.resolver.channel_unit(
            x_channel
        )

        for canonical_name in y_channels:
            y_data = self.resolver.channel(
                canonical_name
            )

            source_name = (
                self.resolver.source_channel_name(
                    canonical_name
                )
            )

            display_name = self.resolver.display_name(
                canonical_name
            )

            unit = self.resolver.channel_unit(
                canonical_name
            )

            figure.add_trace(
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    name=self._trace_name(
                        display_name,
                        unit,
                    ),
                    mode="lines",
                    hovertemplate=self._hover_template(
                        x_label=x_label,
                        x_unit=x_unit,
                        y_label=display_name,
                        y_unit=unit,
                        source_name=source_name,
                    ),
                )
            )

        figure.update_xaxes(
            title_text=self._axis_title(
                x_label,
                x_unit,
            )
        )

        figure.update_yaxes(
            title_text="Selected telemetry channels"
        )

        return figure

    def create_lap_comparison_plot(
        self,
        laps: Sequence[Lap],
        channels: Sequence[str],
        points: int = 1000,
    ) -> go.Figure:
        comparison = LapComparison(
            self.session
        )

        prepared_laps = comparison.prepare(
            laps=laps,
            channels=channels,
            points=points,
        )

        figure = make_subplots(
            rows=len(channels),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
        )

        for row, canonical_name in enumerate(
            channels,
            start=1,
        ):
            display_name = self.resolver.display_name(
                canonical_name
            )

            unit = self.resolver.channel_unit(
                canonical_name
            )

            for lap_number, dataframe in prepared_laps.items():
                figure.add_trace(
                    go.Scatter(
                        x=dataframe["lap_distance"],
                        y=dataframe[canonical_name],
                        name=f"Lap {lap_number} — {display_name}",
                        mode="lines",
                        legendgroup=f"lap-{lap_number}",
                        hovertemplate=(
                            f"Lap {lap_number}"
                            "<br>"
                            f"{display_name}: %{{y:.3f}}"
                            f"{f' {unit}' if unit else ''}"
                            "<br>"
                            "Lap Distance: %{x:.1f} m"
                            "<extra></extra>"
                        ),
                    ),
                    row=row,
                    col=1,
                )

            figure.update_yaxes(
                title_text=self._axis_title(
                    display_name,
                    unit,
                ),
                row=row,
                col=1,
            )

        figure.update_xaxes(
            title_text="Lap Distance [m]",
            row=len(channels),
            col=1,
        )

        figure.update_layout(
            title="Lap Comparison",
            hovermode="x unified",
            height=max(
                500,
                250 * len(channels),
            ),
            margin=dict(
                l=70,
                r=40,
                t=70,
                b=60,
            ),
        )

        return figure

    @staticmethod
    def _axis_title(
        label: str,
        unit: str | None,
    ) -> str:
        if unit:
            return f"{label} [{unit}]"

        return label

    @staticmethod
    def _trace_name(
        label: str,
        unit: str | None,
    ) -> str:
        if unit:
            return f"{label} [{unit}]"

        return label

    @staticmethod
    def _hover_template(
        x_label: str,
        x_unit: str | None,
        y_label: str,
        y_unit: str | None,
        source_name: str | None,
    ) -> str:
        x_suffix = f" {x_unit}" if x_unit else ""
        y_suffix = f" {y_unit}" if y_unit else ""
        source = source_name or "Unknown"

        return (
            f"{y_label}: %{{y:.3f}}{y_suffix}"
            "<br>"
            f"{x_label}: %{{x:.3f}}{x_suffix}"
            "<br>"
            f"Source channel: {source}"
            "<extra></extra>"
        )