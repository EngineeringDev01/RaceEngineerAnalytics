from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum

from src.core.telemetry_session import TelemetrySession
from src.domain.car import Car
from src.domain.driver import Driver
from src.domain.stint import Stint
from src.domain.team import Team


class SessionType(StrEnum):
    PRACTICE = "practice"
    QUALIFYING = "qualifying"
    RACE = "race"
    WARM_UP = "warm_up"
    TEST = "test"
    SIMULATION = "simulation"
    OTHER = "other"


@dataclass
class RaceSession:
    name: str
    session_type: SessionType
    car: Car
    team: Team | None = None
    drivers: list[Driver] = field(default_factory=list)
    start_time: datetime | None = None
    telemetry_sessions: list[TelemetrySession] = field(default_factory=list)
    stints: list[Stint] = field(default_factory=list)

    @property
    def telemetry_file_count(self) -> int:
        return len(self.telemetry_sessions)

    @property
    def stint_count(self) -> int:
        return len(self.stints)

    @property
    def lap_count(self) -> int:
        return sum(stint.lap_count for stint in self.stints)

    def add_telemetry(
        self,
        telemetry_session: TelemetrySession,
    ) -> None:
        self.telemetry_sessions.append(telemetry_session)

    def add_stint(
        self,
        stint: Stint,
    ) -> None:
        self.stints.append(stint)

    def to_dict(self) -> dict:
        data = asdict(self)

        data["session_type"] = self.session_type.value
        data["telemetry_file_count"] = self.telemetry_file_count
        data["stint_count"] = self.stint_count
        data["lap_count"] = self.lap_count

        return data