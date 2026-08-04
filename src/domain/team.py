from dataclasses import asdict, dataclass


@dataclass
class Team:
    name: str
    country: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)