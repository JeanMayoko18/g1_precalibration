"""
Application configuration loading and validation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    MotionConfiguration,
    RobotConfiguration,
)


# =============================================================================
# PATHS
# =============================================================================


PROJECT_DIRECTORY = (
    Path(__file__).resolve().parent.parent
)

DATA_DIRECTORY = (
    PROJECT_DIRECTORY
    / "data"
)

HISTORY_DIRECTORY = (
    PROJECT_DIRECTORY
    / "history"
)

CONFIG_PATH = (
    DATA_DIRECTORY
    / "precalibration_config.yaml"
)

RESULTS_PATH = (
    DATA_DIRECTORY
    / "precalibration_results.yaml"
)


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================


DEFAULT_CONFIGURATION: dict[str, Any] = {
    "robot": {
        "command_topic": "/cmd_vel",
        "publish_rate_hz": 45.0,
        "countdown_sec": 3,
        "stop_command_count": 30,
        "maximum_duration_sec": 120.0,
    },
    "motions": {
        "straight_4m": {
            "label": "Straight 4 m",
            "linear_x": 0.12,
            "angular_z": 0.0,
            "target_type": "distance",
            "target_value": 4.0,
            "target_unit": "m",
        },
        "straight_2m": {
            "label": "Straight 2 m",
            "linear_x": 0.12,
            "angular_z": 0.0,
            "target_type": "distance",
            "target_value": 2.0,
            "target_unit": "m",
        },
        "rotate_left": {
            "label": "Rotate Left 90°",
            "linear_x": 0.0,
            "angular_z": 0.20,
            "target_type": "angle",
            "target_value": 90.0,
            "target_unit": "deg",
        },
        "rotate_right": {
            "label": "Rotate Right 90°",
            "linear_x": 0.0,
            "angular_z": -0.20,
            "target_type": "angle",
            "target_value": 90.0,
            "target_unit": "deg",
        },
    },
}


DEFAULT_RESULTS: dict[str, Any] = {
    motion_name: {
        "trials": [],
        "validated_duration_sec": None,
        "validations": [],
    }
    for motion_name in DEFAULT_CONFIGURATION["motions"]
}


# =============================================================================
# YAML INPUT / OUTPUT
# =============================================================================


def load_yaml(
    path: Path,
) -> dict[str, Any]:
    """
    Load one YAML mapping.
    """
    if not path.exists():
        return {}

    try:
        data = yaml.safe_load(
            path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        yaml.YAMLError,
    ) as exc:
        raise RuntimeError(
            f"Unable to load YAML file '{path}': {exc}"
        ) from exc

    if data is None:
        return {}

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            f"YAML root must be a mapping: {path}"
        )

    return data


def save_yaml(
    path: Path,
    data: dict[str, Any],
) -> None:
    """
    Save one mapping as UTF-8 YAML.
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


# =============================================================================
# INITIALIZATION
# =============================================================================


def initialize_project_data() -> None:
    """
    Create required directories and default YAML files.
    """
    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not CONFIG_PATH.exists():
        save_yaml(
            CONFIG_PATH,
            DEFAULT_CONFIGURATION,
        )

    if not RESULTS_PATH.exists():
        save_yaml(
            RESULTS_PATH,
            DEFAULT_RESULTS,
        )


# =============================================================================
# VALIDATION HELPERS
# =============================================================================


def require_mapping(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> dict[str, Any]:
    """
    Return one required mapping.
    """
    value = parent.get(
        key
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected mapping '{context}.{key}'."
        )

    return value


def require_string(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> str:
    """
    Return one required non-empty string.
    """
    value = parent.get(
        key
    )

    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise RuntimeError(
            f"Expected non-empty string '{context}.{key}'."
        )

    return value.strip()


def require_float(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> float:
    """
    Return one required numeric value.
    """
    value = parent.get(
        key
    )

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            (
                int,
                float,
            ),
        )
    ):
        raise RuntimeError(
            f"Expected numeric value '{context}.{key}'."
        )

    return float(
        value
    )


def require_positive_float(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> float:
    """
    Return one strictly positive numeric value.
    """
    value = require_float(
        parent,
        key,
        context,
    )

    if value <= 0.0:
        raise RuntimeError(
            f"'{context}.{key}' must be greater than zero."
        )

    return value


def require_non_negative_int(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> int:
    """
    Return one non-negative integer.
    """
    value = parent.get(
        key
    )

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 0
    ):
        raise RuntimeError(
            f"Expected non-negative integer '{context}.{key}'."
        )

    return value


# =============================================================================
# CONFIGURATION OBJECT
# =============================================================================


class Configuration:
    """
    Load and expose the complete pre-calibration configuration.
    """

    def __init__(
        self,
        path: Path = CONFIG_PATH,
    ) -> None:
        initialize_project_data()

        self.path = path.resolve()

        self._raw = load_yaml(
            self.path
        )

        self.robot = self._build_robot_configuration()

        self._motions = self._build_motion_configurations()

    def _build_robot_configuration(
        self,
    ) -> RobotConfiguration:
        """
        Build the validated robot configuration.
        """
        robot = require_mapping(
            self._raw,
            "robot",
            "root",
        )

        command_topic = require_string(
            robot,
            "command_topic",
            "robot",
        )

        if not command_topic.startswith(
            "/"
        ):
            raise RuntimeError(
                "robot.command_topic must be an absolute ROS topic."
            )

        return RobotConfiguration(
            command_topic=command_topic,
            publish_rate_hz=require_positive_float(
                robot,
                "publish_rate_hz",
                "robot",
            ),
            countdown_sec=require_non_negative_int(
                robot,
                "countdown_sec",
                "robot",
            ),
            stop_command_count=require_non_negative_int(
                robot,
                "stop_command_count",
                "robot",
            ),
            maximum_duration_sec=require_positive_float(
                robot,
                "maximum_duration_sec",
                "robot",
            ),
        )

    def _build_motion_configurations(
        self,
    ) -> dict[str, MotionConfiguration]:
        """
        Build every validated motion configuration.
        """
        motions = require_mapping(
            self._raw,
            "motions",
            "root",
        )

        result: dict[
            str,
            MotionConfiguration,
        ] = {}

        for motion_name, value in motions.items():
            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    f"Motion '{motion_name}' must be a mapping."
                )

            context = (
                f"motions.{motion_name}"
            )

            target_type = require_string(
                value,
                "target_type",
                context,
            )

            if target_type not in {
                "distance",
                "angle",
            }:
                raise RuntimeError(
                    f"{context}.target_type must be "
                    "'distance' or 'angle'."
                )

            target_value = require_positive_float(
                value,
                "target_value",
                context,
            )

            result[motion_name] = MotionConfiguration(
                name=motion_name,
                label=require_string(
                    value,
                    "label",
                    context,
                ),
                linear_x=require_float(
                    value,
                    "linear_x",
                    context,
                ),
                angular_z=require_float(
                    value,
                    "angular_z",
                    context,
                ),
                target_type=target_type,
                target_value=target_value,
                target_unit=require_string(
                    value,
                    "target_unit",
                    context,
                ),
            )

        if not result:
            raise RuntimeError(
                "No motion configuration was defined."
            )

        return result

    def motion(
        self,
        motion_name: str,
    ) -> MotionConfiguration:
        """
        Return one configured motion.
        """
        try:
            return self._motions[
                motion_name
            ]
        except KeyError as exc:
            raise KeyError(
                f"Unknown motion: {motion_name}"
            ) from exc

    def motions(
        self,
    ) -> tuple[
        MotionConfiguration,
        ...,
    ]:
        """
        Return every configured motion.
        """
        return tuple(
            self._motions.values()
        )

    def motion_names(
        self,
    ) -> tuple[str, ...]:
        """
        Return every configured motion name.
        """
        return tuple(
            self._motions
        )

    @property
    def results_path(
        self,
    ) -> Path:
        """
        Return the persistent results path.
        """
        return RESULTS_PATH

    @property
    def history_directory(
        self,
    ) -> Path:
        """
        Return the history output directory.
        """
        return HISTORY_DIRECTORY