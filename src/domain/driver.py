from dataclasses import asdict, dataclass


@dataclass
class Driver:
    first_name: str
    last_name: str
    abbreviation: str | None = None
    nationality: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        return asdict(self)