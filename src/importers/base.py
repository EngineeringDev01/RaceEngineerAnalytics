from abc import ABC, abstractmethod
from pathlib import Path

from src.core.telemetry_session import TelemetrySession


class TelemetryImporter(ABC):
    source_system: str = "Unknown"

    @abstractmethod
    def can_import(self, file_path: Path) -> bool:
        """Return True when this importer supports the supplied file."""
        raise NotImplementedError

    @abstractmethod
    def load(self, file_path: Path) -> TelemetrySession:
        """Load the supplied file into the common telemetry model."""
        raise NotImplementedError