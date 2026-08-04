from dataclasses import asdict, dataclass, field
from datetime import date

from src.domain.circuit import Circuit


@dataclass
class Event:
    name: str
    circuit: Circuit
    start_date: date | None = None
    end_date: date | None = None
    sessions: list[str] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        if self.start_date is None:
            return self.name

        return f"{self.name} - {self.start_date.isoformat()}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["display_name"] = self.display_name
        return data