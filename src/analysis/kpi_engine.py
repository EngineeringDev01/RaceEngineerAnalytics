from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.core.kpi import KPI
from src.core.telemetry_resolver import TelemetryResolver
from src.core.telemetry_session import TelemetrySession


class KPIEngine:
    """
    Calculate engineering KPIs from a telemetry session.

    All KPI calculations use canonical channels through TelemetryResolver,
    so the engine remains independent from MoTeC, Bosch, Marelli,
    Generic CSV, or future telemetry sources.
    """

    def __init__(
        self,
        session: TelemetrySession,
    ) -> None:
        self.session = session
        self.resolver = TelemetryResolver(session)

    def calculate(self) -> dict[str, list[KPI]]:
        """
        Calculate every currently supported KPI category.
        """
        return {
            "performance": self.performance(),
            "driver_inputs": self.driver_inputs(),
            "vehicle_dynamics": self.vehicle_dynamics(),
        }

    def performance(self) -> list[KPI]:
        """
        Calculate vehicle-performance KPIs.

        KPIs currently supported:
        - Maximum Speed
        - Average Speed
        - Minimum Speed
        - Maximum Engine RPM
        - Average Engine RPM
        """

        kpis: list[KPI] = []

        self._append_if_available(
            kpis,
            self._create_stat_kpi(
                canonical_name="speed",
                name="Maximum Speed",
                category="Performance",
                statistic=lambda values: values.max(),
                description="Maximum recorded vehicle speed.",
            ),
        )

        self._append_if_available(
            kpis,
            self._create_stat_kpi(
                canonical_name="speed",
                name="Average Speed",
                category="Performance",
                statistic=lambda values: values.mean(),
                description="Average recorded vehicle speed.",
            ),
        )

        self._append_if_available(
            kpis,
            self._create_stat_kpi(
                canonical_name="speed",
                name="Minimum Speed",
                category="Performance",
                statistic=lambda values: values.min(),
                description="Minimum recorded vehicle speed.",
            ),
        )

        self._append_if_available(
            kpis,
            self._create_stat_kpi(
                canonical_name="rpm",
                name="Maximum Engine RPM",
                category="Performance",
                statistic=lambda values: values.max(),
                description="Maximum recorded engine speed.",
            ),
        )

        self._append_if_available(
            kpis,
            self._create_stat_kpi(
                canonical_name="rpm",
                name="Average Engine RPM",
                category="Performance",
                statistic=lambda values: values.mean(),
                description="Average recorded engine speed.",
            ),
        )

        return kpis


    def driver_inputs(self) -> list[KPI]:
        """
        Calculate driver-input KPIs.

        KPIs currently supported:
        - Average Throttle
        - Maximum Throttle
        - Full Throttle Percentage
        - Maximum Brake Pressure
        - Average Brake Pressure
        - Brake Usage Percentage
        """

        kpis: list[KPI] = []

        # --------------------------------------------------
        # Throttle
        # --------------------------------------------------

        throttle = self._numeric_channel("throttle")

        if throttle is not None:

            source_channel = (
                self.resolver.source_channel_name("throttle")
                or ""
            )

            unit = (
                self.resolver.channel_unit("throttle")
                or "%"
            )

            kpis.append(
                KPI(
                    name="Average Throttle",
                    value=float(throttle.mean()),
                    unit=unit,
                    category="Driver Inputs",
                    source_channel=source_channel,
                    description="Average throttle position during the telemetry window.",
                )
            )

            kpis.append(
                KPI(
                    name="Maximum Throttle",
                    value=float(throttle.max()),
                    unit=unit,
                    category="Driver Inputs",
                    source_channel=source_channel,
                    description="Maximum recorded throttle position.",
                )
            )

            full_throttle_percentage = float(
                (throttle >= 98.0).mean()
                * 100.0
            )

            kpis.append(
                KPI(
                    name="Full Throttle",
                    value=full_throttle_percentage,
                    unit="%",
                    category="Driver Inputs",
                    source_channel=source_channel,
                    description=(
                        "Percentage of samples where throttle "
                        "position is at least 98%."
                    ),
                )
            )

        # --------------------------------------------------
        # Brake
        # --------------------------------------------------

        brake_canonical_name = self._best_brake_channel()

        if brake_canonical_name is not None:

            brake = self._numeric_channel(
                brake_canonical_name
            )

            if brake is not None:

                source_channel = (
                    self.resolver.source_channel_name(
                        brake_canonical_name
                    )
                    or ""
                )

                unit = (
                    self.resolver.channel_unit(
                        brake_canonical_name
                    )
                    or "bar"
                )

                kpis.append(
                    KPI(
                        name="Maximum Brake Pressure",
                        value=float(brake.max()),
                        unit=unit,
                        category="Driver Inputs",
                        source_channel=source_channel,
                        description=(
                            "Maximum recorded brake pressure."
                        ),
                    )
                )

                kpis.append(
                    KPI(
                        name="Average Brake Pressure",
                        value=float(brake.mean()),
                        unit=unit,
                        category="Driver Inputs",
                        source_channel=source_channel,
                        description=(
                            "Average brake pressure over the "
                            "complete telemetry window."
                        ),
                    )
                )

                brake_usage_percentage = float(
                    (brake > 1.0).mean()
                    * 100.0
                )

                kpis.append(
                    KPI(
                        name="Brake Usage",
                        value=brake_usage_percentage,
                        unit="%",
                        category="Driver Inputs",
                        source_channel=source_channel,
                        description=(
                            "Percentage of samples where brake "
                            "pressure is greater than 1 bar."
                        ),
                    )
                )

        return kpis

    def _best_brake_channel(
        self,
    ) -> str | None:
        """
        Select the best available brake-pressure channel.

        Priority:
        1. Front brake pressure
        2. Generic brake pressure
        3. Rear brake pressure
        """

        for canonical_name in (
            "brake_front",
            "brake",
            "brake_rear",
        ):
            if self.resolver.has_channel(
                canonical_name
            ):
                return canonical_name

        return None

    def vehicle_dynamics(self) -> list[KPI]:
        """
        Vehicle-dynamics KPIs.

        Implemented in Sprint 2.7.5.
        """
        return []

    def _numeric_channel(
        self,
        canonical_name: str,
    ) -> pd.Series | None:
        """
        Return a canonical channel converted to numeric data.

        Missing channels return None rather than raising an exception,
        allowing KPI calculations to gracefully support telemetry files
        with different available signals.
        """
        if not self.resolver.has_channel(canonical_name):
            return None

        values = pd.to_numeric(
            self.resolver.channel(canonical_name),
            errors="coerce",
        ).dropna()

        if values.empty:
            return None

        return values

    def _create_stat_kpi(
        self,
        canonical_name: str,
        name: str,
        category: str,
        statistic: Callable[[pd.Series], float],
        description: str = "",
    ) -> KPI | None:
        """
        Build a KPI from a numeric telemetry channel.
        """
        values = self._numeric_channel(
            canonical_name
        )

        if values is None:
            return None

        value = float(statistic(values))

        source_channel = (
            self.resolver.source_channel_name(
                canonical_name
            )
            or ""
        )

        unit = (
            self.resolver.channel_unit(
                canonical_name
            )
            or ""
        )

        return KPI(
            name=name,
            value=value,
            unit=unit,
            category=category,
            source_channel=source_channel,
            description=description,
        )

    @staticmethod
    def _append_if_available(
        collection: list[KPI],
        kpi: KPI | None,
    ) -> None:
        """
        Append a KPI only when the required telemetry channel exists.
        """
        if kpi is not None:
            collection.append(kpi)