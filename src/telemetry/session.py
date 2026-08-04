from dataclasses import dataclass
import pandas as pd

from .channels import find_available_channels


@dataclass
class TelemetrySession:
    filename: str
    dataframe: pd.DataFrame

    @property
    def channels(self):
        return list(self.dataframe.columns)

    @property
    def samples(self):
        return len(self.dataframe)

    def summary(self):
        print(f"File: {self.filename}")
        print(f"Samples: {self.samples}")
        print(f"Channels: {len(self.channels)}")

        print("\nAvailable channels:")

        for channel in self.channels:
            print(f" - {channel}")

    def detect_channels(self):

        return find_available_channels(
            self.dataframe
        )