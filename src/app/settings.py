from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ApplicationSettings:
    name: str
    version: str


@dataclass(frozen=True)
class TelemetrySettings:
    temporary_folder_name: str


@dataclass(frozen=True)
class EngineeringSettings:
    full_throttle_threshold_pct: float
    brake_active_threshold_bar: float


@dataclass(frozen=True)
class PlottingSettings:
    default_x_axis: str
    separate_axes: bool
    track_map_height: int


@dataclass(frozen=True)
class DatabaseSettings:
    enabled: bool
    host: str
    port: int
    database: str
    username: str
    password: str


@dataclass(frozen=True)
class Settings:
    application: ApplicationSettings
    telemetry: TelemetrySettings
    engineering: EngineeringSettings
    plotting: PlottingSettings
    database: DatabaseSettings


class SettingsLoader:
    """
    Load and validate application configuration from YAML.
    """

    def __init__(
        self,
        config_path: str | Path,
    ) -> None:
        self.config_path = Path(config_path)

    def load(self) -> Settings:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        raw_config = self._read_yaml()

        return Settings(
            application=self._load_application_settings(
                raw_config
            ),
            telemetry=self._load_telemetry_settings(
                raw_config
            ),
            engineering=self._load_engineering_settings(
                raw_config
            ),
            plotting=self._load_plotting_settings(
                raw_config
            ),
            database=self._load_database_settings(
                raw_config
            ),
        )

    def _read_yaml(self) -> dict[str, Any]:
        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            content = yaml.safe_load(file) or {}

        if not isinstance(content, dict):
            raise ValueError(
                "Configuration root must be a dictionary."
            )

        return content

    @staticmethod
    def _section(
        config: dict[str, Any],
        name: str,
    ) -> dict[str, Any]:
        section = config.get(name)

        if section is None:
            raise KeyError(
                f"Missing configuration section: '{name}'."
            )

        if not isinstance(section, dict):
            raise TypeError(
                f"Configuration section '{name}' "
                "must be a dictionary."
            )

        return section

    def _load_application_settings(
        self,
        config: dict[str, Any],
    ) -> ApplicationSettings:
        section = self._section(
            config,
            "application",
        )

        return ApplicationSettings(
            name=str(
                section.get(
                    "name",
                    "Race Engineer Analytics",
                )
            ),
            version=str(
                section.get(
                    "version",
                    "0.0.0",
                )
            ),
        )

    def _load_telemetry_settings(
        self,
        config: dict[str, Any],
    ) -> TelemetrySettings:
        section = self._section(
            config,
            "telemetry",
        )

        return TelemetrySettings(
            temporary_folder_name=str(
                section.get(
                    "temporary_folder_name",
                    "race_engineer_analytics",
                )
            )
        )

    def _load_engineering_settings(
        self,
        config: dict[str, Any],
    ) -> EngineeringSettings:
        section = self._section(
            config,
            "engineering",
        )

        return EngineeringSettings(
            full_throttle_threshold_pct=float(
                section.get(
                    "full_throttle_threshold_pct",
                    98.0,
                )
            ),
            brake_active_threshold_bar=float(
                section.get(
                    "brake_active_threshold_bar",
                    1.0,
                )
            ),
        )

    def _load_plotting_settings(
        self,
        config: dict[str, Any],
    ) -> PlottingSettings:
        section = self._section(
            config,
            "plotting",
        )

        return PlottingSettings(
            default_x_axis=str(
                section.get(
                    "default_x_axis",
                    "distance",
                )
            ),
            separate_axes=bool(
                section.get(
                    "separate_axes",
                    True,
                )
            ),
            track_map_height=int(
                section.get(
                    "track_map_height",
                    500,
                )
            ),
        )

    def _load_database_settings(
        self,
        config: dict[str, Any],
    ) -> DatabaseSettings:
        section = self._section(
            config,
            "database",
        )

        return DatabaseSettings(
            enabled=bool(
                section.get(
                    "enabled",
                    False,
                )
            ),
            host=str(
                section.get(
                    "host",
                    "localhost",
                )
            ),
            port=int(
                section.get(
                    "port",
                    3306,
                )
            ),
            database=str(
                section.get(
                    "database",
                    "race_engineering",
                )
            ),
            username=str(
                section.get(
                    "username",
                    "",
                )
            ),
            password=str(
                section.get(
                    "password",
                    "",
                )
            ),
        )