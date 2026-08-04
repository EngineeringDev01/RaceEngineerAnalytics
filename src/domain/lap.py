from dataclasses import asdict, dataclass, field


@dataclass
class Lap:
    number: int
    lap_time_s: float | None = None
    sector_times_s: list[float] = field(default_factory=list)
    valid: bool = True
    in_lap: bool = False
    out_lap: bool = False
    telemetry_start_index: int | None = None
    telemetry_end_index: int | None = None

    @property
    def sector_count(self) -> int:
        return len(self.sector_times_s)

    def to_dict(self) -> dict:
        return asdict(self)