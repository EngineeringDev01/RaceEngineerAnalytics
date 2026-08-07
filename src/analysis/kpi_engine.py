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
        Vehicle performance KPIs.

        Implemented in Sprint 2.7.3.
        """
        return []

    def driver_inputs(self) -> list[KPI]:
        """
        Driver-input KPIs.

        Implemented in Sprint 2.7.4.
        """
        return []

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