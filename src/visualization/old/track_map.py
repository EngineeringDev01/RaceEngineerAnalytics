from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.core.telemetry_resolver import TelemetryResolver
from src.core.telemetry_session import TelemetrySession


class TrackMapPlotter:
    """Create track maps from Cartesian or GPS telemetry."""

    def __init__(
        self,
        session: TelemetrySession,
    ) -> None:
        self.session = session
        self.resolver = TelemetryResolver(session)

    def create_track_map(
        self,
        selected_index: int | None = None,
        color_channel: str | None = "speed",
    ) -> go.Figure:
        if (
            self.resolver.has_channel("track_x")
            and self.resolver.has_channel("track_y")
        ):
            return self._create_cartesian_map(
                selected_index=selected_index,
                color_channel=color_channel,
            )

        if (
            self.resolver.has_channel("gps_latitude")
            and self.resolver.has_channel("gps_longitude")
        ):
            return self._create_geographic_map(
                selected_index=selected_index,
                color_channel=color_channel,
            )

        raise KeyError(
            "No supported track-position channels are available."
        )

    def _create_cartesian_map(
        self,
        selected_index: int | None,
        color_channel: str | None,
    ) -> go.Figure:
        x_full = pd.to_numeric(
            self.resolver.track_x(),
            errors="coerce",
        )

        y_full = pd.to_numeric(
            self.resolver.track_y(),
            errors="coerce",
        )

        valid_mask = x_full.notna() & y_full.notna()

        x = x_full[valid_mask]
        y = y_full[valid_mask]

        if x.empty:
            raise ValueError(
                "Track-position channels contain no valid samples."
            )

        marker: dict = {
            "size": 5,
        }

        customdata = None
        hovertemplate = (
            "X: %{x:.2f} m"
            "<br>"
            "Y: %{y:.2f} m"
            "<extra></extra>"
        )

        if (
            color_channel
            and self.resolver.has_channel(color_channel)
        ):
            color_values = pd.to_numeric(
                self.resolver.channel(color_channel),
                errors="coerce",
            )[valid_mask]

            unit = (
                self.resolver.channel_unit(color_channel)
                or ""
            )

            display_name = self.resolver.display_name(
                color_channel
            )

            marker.update(
                {
                    "color": color_values,
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {
                        "title": (
                            f"{display_name}"
                            f"{f' [{unit}]' if unit else ''}"
                        )
                    },
                }
            )

            customdata = color_values

            hovertemplate = (
                "X: %{x:.2f} m"
                "<br>"
                "Y: %{y:.2f} m"
                "<br>"
                f"{display_name}: %{{customdata:.2f}}"
                f"{f' {unit}' if unit else ''}"
                "<extra></extra>"
            )

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name="Racing Line",
                line={
                    "width": 2,
                },
                marker=marker,
                customdata=customdata,
                hovertemplate=hovertemplate,
            )
        )

        if selected_index is not None:
            selected_index = self._safe_index(
                selected_index
            )

            selected_x = x_full.iloc[selected_index]
            selected_y = y_full.iloc[selected_index]

            if (
                pd.notna(selected_x)
                and pd.notna(selected_y)
            ):
                figure.add_trace(
                    go.Scatter(
                        x=[selected_x],
                        y=[selected_y],
                        mode="markers",
                        name="Selected Position",
                        marker={
                            "size": 15,
                            "symbol": "circle",
                            "line": {
                                "width": 2,
                            },
                        },
                        hovertemplate=(
                            "Selected sample"
                            "<br>"
                            "X: %{x:.2f} m"
                            "<br>"
                            "Y: %{y:.2f} m"
                            "<extra></extra>"
                        ),
                    )
                )

        figure.update_layout(
            title="Track Map",
            xaxis_title="Track X [m]",
            yaxis_title="Track Y [m]",
            height=650,
            hovermode="closest",
            margin={
                "l": 40,
                "r": 40,
                "t": 70,
                "b": 50,
            },
        )

        figure.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

        return figure

    def _create_geographic_map(
        self,
        selected_index: int | None,
        color_channel: str | None,
    ) -> go.Figure:
        latitude_full = pd.to_numeric(
            self.resolver.gps_latitude(),
            errors="coerce",
        )

        longitude_full = pd.to_numeric(
            self.resolver.gps_longitude(),
            errors="coerce",
        )

        valid_mask = (
            latitude_full.notna()
            & longitude_full.notna()
        )

        latitude = latitude_full[valid_mask]
        longitude = longitude_full[valid_mask]

        if latitude.empty:
            raise ValueError(
                "GPS channels contain no valid samples."
            )

        marker: dict = {
            "size": 6,
        }

        if (
            color_channel
            and self.resolver.has_channel(color_channel)
        ):
            color_values = pd.to_numeric(
                self.resolver.channel(color_channel),
                errors="coerce",
            )[valid_mask]

            marker.update(
                {
                    "color": color_values,
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {
                        "title": self.resolver.display_name(
                            color_channel
                        )
                    },
                }
            )

        figure = go.Figure()

        figure.add_trace(
            go.Scattergeo(
                lat=latitude,
                lon=longitude,
                mode="lines+markers",
                name="Racing Line",
                marker=marker,
            )
        )

        if selected_index is not None:
            selected_index = self._safe_index(
                selected_index
            )

            selected_latitude = latitude_full.iloc[
                selected_index
            ]

            selected_longitude = longitude_full.iloc[
                selected_index
            ]

            if (
                pd.notna(selected_latitude)
                and pd.notna(selected_longitude)
            ):
                figure.add_trace(
                    go.Scattergeo(
                        lat=[selected_latitude],
                        lon=[selected_longitude],
                        mode="markers",
                        name="Selected Position",
                        marker={
                            "size": 15,
                        },
                    )
                )

        figure.update_geos(
            fitbounds="locations",
            visible=False,
        )

        figure.update_layout(
            title="GPS Track Map",
            height=650,
            margin={
                "l": 20,
                "r": 20,
                "t": 70,
                "b": 20,
            },
        )

        return figure

    def _safe_index(
        self,
        index: int,
    ) -> int:
        return max(
            0,
            min(
                int(index),
                self.session.samples - 1,
            ),
        )