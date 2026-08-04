from pathlib import Path

from src.telemetry.importer import TelemetryImporter

from src.analysis.performance import PerformanceAnalyzer


PROJECT_ROOT = Path(__file__).resolve().parent


def main():

    print("=" * 50)
    print("Race Engineer Analytics")
    print("=" * 50)

    print(f"Project folder: {PROJECT_ROOT}")

    csv_file = PROJECT_ROOT / "data" / "raw" / "session.csv"

    print(f"\nLoading telemetry: {csv_file.name}")

    session = TelemetryImporter.load_motec_csv(csv_file)

    print("\nSession Summary")
    print("-" * 50)

    session.summary()

    performance = PerformanceAnalyzer(
    session.dataframe
    )

    performance.summary()

    print("\nDetected Engineering Channels")
    print("-" * 50)

    channels = session.detect_channels()

    for group, values in channels.items():

        print(f"\n{group.upper()}")

        print(values)


if __name__ == "__main__":
    main()