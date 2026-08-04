from dataclasses import asdict, dataclass, field

from src.domain.championship import Championship


@dataclass
class Season:
    year: int
    championship: Championship
    events: list[str] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return f"{self.championship.name} {self.year}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["display_name"] = self.display_name
        return data