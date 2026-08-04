from dataclasses import asdict, dataclass


@dataclass
class Car:
    manufacturer: str
    model: str
    category: str
    number: str | None = None
    chassis_number: str | None = None
    team_name: str | None = None

    @property
    def display_name(self) -> str:
        number = f" #{self.number}" if self.number else ""
        return f"{self.manufacturer} {self.model}{number}"

    def to_dict(self) -> dict:
        return asdict(self)