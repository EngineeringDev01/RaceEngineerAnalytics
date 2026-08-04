from pathlib import Path

from src.core.telemetry_session import TelemetrySession
from src.importers.factory import ImporterFactory


class TelemetryService:
    def __init__(
        self,
        importer_factory: ImporterFactory | None = None,
    ) -> None:
        self.importer_factory = importer_factory or ImporterFactory()

    def load(
        self,
        file_path: str | Path,
    ) -> TelemetrySession:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Telemetry file not found: {path}"
            )

        session = self.importer_factory.load(path)

        self._validate_session(session)

        return session

    @staticmethod
    def _validate_session(
        session: TelemetrySession,
    ) -> None:
        if session.dataframe.empty:
            raise ValueError(
                f"Telemetry session '{session.filename}' contains no samples."
            )

        if session.samples <= 0:
            raise ValueError(
                f"Telemetry session '{session.filename}' has no valid samples."
            )

        if not session.channels:
            raise ValueError(
                f"Telemetry session '{session.filename}' has no channels."
            )