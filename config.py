from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

DATABASE_NAME = "race_engineering"

DEFAULT_DRIVER = "Unknown"

DEFAULT_CAR = "LMP2"