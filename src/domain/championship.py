from dataclasses import asdict, dataclass


@dataclass
class Championship:
    name: str
    organizer: str | None = None
    category: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)