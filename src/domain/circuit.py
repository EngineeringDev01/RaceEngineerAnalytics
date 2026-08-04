from dataclasses import asdict, dataclass


@dataclass
class Circuit:
    name: str
    country: str
    length_m: float | None = None
    turns: int | None = None
    pit_speed_limit_kph: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)