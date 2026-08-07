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

        valid_x = x_full[valid_mask]
        valid_y = y_full[valid_mask]

        if valid_x.empty:
            raise ValueError(
                "Track-position channels contain no valid samples."
            )

        x_mean = float(valid_x.mean())
        y_mean = float(valid_y.mean())

        x = valid_x - x_mean
        y = valid_y - y_mean

        figure = go.Figure()

        # Clean trajectory line.
        figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Trajectory",
                line={"width": 3},
                hoverinfo="skip",
            )
        )

        # Optional colour layer.
        if (
            color_channel
            and self.resolver.has_channel(color_channel)
        ):
            color_values = pd.to_numeric(
                self.resolver.channel(color_channel),
                errors="coerce",
            )[valid_mask]

            display_name = self.resolver.display_name(
                color_channel
            )
            unit = self.resolver.channel_unit(
                color_channel
            ) or ""

            figure.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    name=display_name,
                    marker={
                        "size": 5,
                        "color": color_values,
                        "colorscale": "Viridis",
                        "showscale": True,
                        "colorbar": {
                            "title": (
                                f"{display_name}"
                                f"{f' [{unit}]' if unit else ''}"
                            )
                        },
                    },
                    customdata=color_values,
                    hovertemplate=(
                        "X: %{x:.2f} m"
                        "<br>"
                        "Y: %{y:.2f} m"
                        "<br>"
                        f"{display_name}: %{{customdata:.2f}}"
                        f"{f' {unit}' if unit else ''}"
                        "<extra></extra>"
                    ),
                )
            )

        # Synchronized selected sample.
        if selected_index is not None:
            safe_index = self._safe_index(selected_index)

            selected_x = x_full.iloc[safe_index]
            selected_y = y_full.iloc[safe_index]

            if (
                pd.notna(selected_x)
                and pd.notna(selected_y)
            ):
                figure.add_trace(
                    go.Scatter(
                        x=[float(selected_x) - x_mean],
                        y=[float(selected_y) - y_mean],
                        mode="markers",
                        name="Selected Position",
                        marker={
                            "size": 15,
                            "symbol": "circle",
                            "line": {"width": 2},
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
            xaxis_title="Relative X [m]",
            yaxis_title="Relative Y [m]",
            height=500,
            hovermode="closest",
            margin={
                "l": 40,
                "r": 40,
                "t": 70,
                "b": 50,
            },
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.01,
                "xanchor": "left",
                "x": 0,
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

        figure = go.Figure()

        figure.add_trace(
            go.Scattergeo(
                lat=latitude,
                lon=longitude,
                mode="lines",
                name="Trajectory",
                line={"width": 3},
                hoverinfo="skip",
            )
        )

        if (
            color_channel
            and self.resolver.has_channel(color_channel)
        ):
            color_values = pd.to_numeric(
                self.resolver.channel(color_channel),
                errors="coerce",
            )[valid_mask]

            display_name = self.resolver.display_name(
                color_channel
            )
            unit = self.resolver.channel_unit(
                color_channel
            ) or ""

            figure.add_trace(
                go.Scattergeo(
                    lat=latitude,
                    lon=longitude,
                    mode="markers",
                    name=display_name,
                    marker={
                        "size": 6,
                        "color": color_values,
                        "colorscale": "Viridis",
                        "showscale": True,
                        "colorbar": {
                            "title": (
                                f"{display_name}"
                                f"{f' [{unit}]' if unit else ''}"
                            )
                        },
                    },
                    customdata=color_values,
                    hovertemplate=(
                        "Latitude: %{lat:.6f}"
                        "<br>"
                        "Longitude: %{lon:.6f}"
                        "<br>"
                        f"{display_name}: %{{customdata:.2f}}"
                        f"{f' {unit}' if unit else ''}"
                        "<extra></extra>"
                    ),
                )
            )

        if selected_index is not None:
            safe_index = self._safe_index(selected_index)

            selected_latitude = latitude_full.iloc[safe_index]
            selected_longitude = longitude_full.iloc[safe_index]

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
                        marker={"size": 15},
                    )
                )

        figure.update_geos(
            fitbounds="locations",
            visible=False,
        )

        figure.update_layout(
            title="GPS Track Map",
            height=500,
            margin={
                "l": 20,
                "r": 20,
                "t": 70,
                "b": 20,
            },
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.01,
                "xanchor": "left",
                "x": 0,
            },
        )

        return figure

    def trajectory_quality(self) -> dict[str, float | bool]:
        x = pd.to_numeric(
            self.resolver.track_x(),
            errors="coerce",
        )
        y = pd.to_numeric(
            self.resolver.track_y(),
            errors="coerce",
        )

        valid = x.notna() & y.notna()
        x = x[valid]
        y = y[valid]

        if len(x) < 2:
            return {
                "closed": False,
                "closure_distance_m": float("nan"),
                "trajectory_length_m": 0.0,
            }

        dx = x.diff()
        dy = y.diff()

        trajectory_length = (
            (dx.pow(2) + dy.pow(2)).pow(0.5)
        ).sum()

        closure_distance = (
            (x.iloc[-1] - x.iloc[0]) ** 2
            + (y.iloc[-1] - y.iloc[0]) ** 2
        ) ** 0.5

        closed = closure_distance < max(
            30.0,
            trajectory_length * 0.02,
        )

        return {
            "closed": bool(closed),
            "closure_distance_m": float(closure_distance),
            "trajectory_length_m": float(trajectory_length),
        }

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
