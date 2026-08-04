import pandas as pd


class PerformanceAnalyzer:

    def __init__(self, dataframe: pd.DataFrame):

        self.data = dataframe


    def max_speed(self):

        return self.data["Speed FL"].max()


    def max_rpm(self):

        return self.data["Engine RPM"].max()


    def max_lateral_g(self):

        return self.data["G Force Lat"].max()


    def max_longitudinal_g(self):

        return self.data["G Force Long"].max()


    def summary(self):

        print("\nPerformance Summary")
        print("-" * 50)

        print(
            f"Max Speed: {self.max_speed():.1f} km/h"
        )

        print(
            f"Max RPM: {self.max_rpm():.0f}"
        )

        print(
            f"Max Lateral G: {self.max_lateral_g():.2f}"
        )

        print(
            f"Max Longitudinal G: {self.max_longitudinal_g():.2f}"
        )