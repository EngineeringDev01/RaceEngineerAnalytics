from pathlib import Path

from src.analysis.performance import PerformanceAnalyzer
from src.services.telemetry_service import TelemetryService


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("=" * 50)
    print("Race Engineer Analytics")
    print("=" * 50)

    print(f"Project folder: {PROJECT_ROOT}")

    csv_file = PROJECT_ROOT / "data" / "raw" / "session.csv"

    print(f"\nLoading telemetry: {csv_file.name}")

    telemetry_service = TelemetryService()
    session = telemetry_service.load(csv_file)

    print("\nSession Summary")
    print("-" * 50)

    summary = session.summary()

    for key, value in summary.items():
        if key != "resolved_channels":
            print(f"{key}: {value}")

    performance = PerformanceAnalyzer(
        session.dataframe
    )

    performance.summary()

    print("\nResolved Engineering Channels")
    print("-" * 50)

    channels = session.resolved_channels()

    for canonical_name, source_name in channels.items():
        print(f"{canonical_name}: {source_name}")


if __name__ == "__main__":
    main()