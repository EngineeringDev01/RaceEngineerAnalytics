from dataclasses import asdict, dataclass, field

from src.domain.lap import Lap


@dataclass
class Stint:
    number: int
    driver_name: str | None = None
    tyre_set: str | None = None
    fuel_start_kg: float | None = None
    fuel_end_kg: float | None = None
    laps: list[Lap] = field(default_factory=list)

    @property
    def lap_count(self) -> int:
        return len(self.laps)

    @property
    def valid_laps(self) -> list[Lap]:
        return [
            lap
            for lap in self.laps
            if lap.valid and not lap.in_lap and not lap.out_lap
        ]

    def to_dict(self) -> dict:
        return asdict(self)