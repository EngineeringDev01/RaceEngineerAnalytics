from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class KPI:
    """
    Standard engineering KPI representation.

    This object is designed to be reused by:
    - Streamlit dashboards
    - MySQL / SQLAlchemy persistence
    - Grafana
    - Automatic reports
    - Future AI engineering analysis
    """

    name: str
    value: float | int | None
    unit: str = ""
    category: str = ""
    source_channel: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def display_value(self) -> str:
        """
        Return a formatted value suitable for dashboards and reports.
        """
        if self.value is None:
            return "N/A"

        if isinstance(self.value, float):
            formatted_value = f"{self.value:.3f}"
        else:
            formatted_value = str(self.value)

        if self.unit:
            return f"{formatted_value} {self.unit}"

        return formatted_value