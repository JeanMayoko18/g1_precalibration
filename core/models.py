"""
Shared data models for the G1 pre-calibration application.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class RobotConfiguration:
    """Store the ROS command publication configuration."""

    command_topic: str
    publish_rate_hz: float
    countdown_sec: int
    stop_command_count: int
    maximum_duration_sec: float


@dataclass(frozen=True)
class MotionConfiguration:
    """Store the command and physical target for one motion."""

    name: str
    label: str
    linear_x: float
    angular_z: float
    target_type: str
    target_value: float
    target_unit: str


# =============================================================================
# ROS MOTION
# =============================================================================


@dataclass(frozen=True)
class MotionRequest:
    """Describe one motion command execution."""

    motion_name: str
    label: str
    command_topic: str
    linear_x: float
    angular_z: float
    publish_rate_hz: float
    countdown_sec: int
    stop_command_count: int
    maximum_duration_sec: float
    stop_mode: str
    duration_sec: float | None = None


@dataclass(frozen=True)
class MotionResult:
    """Store the result returned by the ROS motion executor."""

    elapsed_sec: float
    publication_count: int
    stop_reason: str


# =============================================================================
# STATISTICS
# =============================================================================


@dataclass(frozen=True)
class StatisticsResult:
    """Store repeatability statistics for one motion."""

    sample_count: int
    minimum_sec: float
    maximum_sec: float
    mean_sec: float
    median_sec: float
    standard_deviation_sec: float
    coefficient_variation_percent: float
    confidence95_half_width_sec: float
    recommended_duration_sec: float
    quality_level: str


# =============================================================================
# PERSISTENT STORAGE
# =============================================================================


@dataclass(frozen=True)
class Trial:
    """Store one operator-controlled pre-calibration trial."""

    id: int
    timestamp: str
    duration_sec: float
    publication_count: int
    stop_reason: str


@dataclass(frozen=True)
class Validation:
    """Store one physical validation result."""

    timestamp: str
    candidate_duration_sec: float
    target_value: float
    measured_value: float
    target_unit: str
    correction_factor: float
    corrected_duration_sec: float
    accepted: bool


@dataclass
class MotionState:
    """Store every persistent result associated with one motion."""

    name: str
    trials: list[Trial] = field(
        default_factory=list
    )
    validated_duration_sec: float | None = None
    validations: list[Validation] = field(
        default_factory=list
    )


# =============================================================================
# CALIBRATION WORKFLOW RESULTS
# =============================================================================


@dataclass(frozen=True)
class TrialResult:
    """Return the complete result of one pre-calibration trial."""

    motion: MotionConfiguration
    motion_result: MotionResult
    statistics: StatisticsResult


@dataclass(frozen=True)
class ValidationPreparation:
    """Describe the fixed-duration motion to execute for validation."""

    motion: MotionConfiguration
    statistics: StatisticsResult
    candidate_duration_sec: float
    request: MotionRequest


@dataclass(frozen=True)
class ValidationResult:
    """Return the calculated result of one physical validation."""

    motion: MotionConfiguration
    candidate_duration_sec: float
    target_value: float
    measured_value: float
    target_unit: str
    correction_factor: float
    corrected_duration_sec: float
    accepted: bool


# =============================================================================
# REPORTING
# =============================================================================


@dataclass(frozen=True)
class MotionReport:
    """Provide all information required to display or export one motion."""

    motion: MotionConfiguration
    state: MotionState
    statistics: StatisticsResult | None


# =============================================================================
# SERIALIZATION
# =============================================================================


def trial_to_mapping(
    trial: Trial,
) -> dict[str, Any]:
    """Convert one Trial to a YAML-compatible mapping."""

    return {
        "id": trial.id,
        "timestamp": trial.timestamp,
        "duration_sec": trial.duration_sec,
        "publication_count": trial.publication_count,
        "stop_reason": trial.stop_reason,
    }


def validation_to_mapping(
    validation: Validation,
) -> dict[str, Any]:
    """Convert one Validation to a YAML-compatible mapping."""

    return {
        "timestamp": validation.timestamp,
        "candidate_duration_sec": (
            validation.candidate_duration_sec
        ),
        "target_value": validation.target_value,
        "measured_value": validation.measured_value,
        "target_unit": validation.target_unit,
        "correction_factor": validation.correction_factor,
        "corrected_duration_sec": (
            validation.corrected_duration_sec
        ),
        "accepted": validation.accepted,
    }


def motion_state_to_mapping(
    state: MotionState,
) -> dict[str, Any]:
    """Convert one MotionState to a YAML-compatible mapping."""

    return {
        "trials": [
            trial_to_mapping(
                trial
            )
            for trial in state.trials
        ],
        "validated_duration_sec": (
            state.validated_duration_sec
        ),
        "validations": [
            validation_to_mapping(
                validation
            )
            for validation in state.validations
        ],
    }


def trial_from_mapping(
    data: dict[str, Any],
) -> Trial:
    """Create one Trial from stored YAML data."""

    return Trial(
        id=int(
            data["id"]
        ),
        timestamp=str(
            data["timestamp"]
        ),
        duration_sec=float(
            data["duration_sec"]
        ),
        publication_count=int(
            data.get(
                "publication_count",
                0,
            )
        ),
        stop_reason=str(
            data.get(
                "stop_reason",
                "unknown",
            )
        ),
    )


def validation_from_mapping(
    data: dict[str, Any],
) -> Validation:
    """Create one Validation from stored YAML data."""

    return Validation(
        timestamp=str(
            data["timestamp"]
        ),
        candidate_duration_sec=float(
            data["candidate_duration_sec"]
        ),
        target_value=float(
            data["target_value"]
        ),
        measured_value=float(
            data["measured_value"]
        ),
        target_unit=str(
            data["target_unit"]
        ),
        correction_factor=float(
            data["correction_factor"]
        ),
        corrected_duration_sec=float(
            data["corrected_duration_sec"]
        ),
        accepted=bool(
            data["accepted"]
        ),
    )


def motion_state_from_mapping(
    motion_name: str,
    data: dict[str, Any],
) -> MotionState:
    """Create one MotionState from stored YAML data."""

    return MotionState(
        name=motion_name,
        trials=[
            trial_from_mapping(
                item
            )
            for item in data.get(
                "trials",
                []
            )
        ],
        validated_duration_sec=(
            float(
                data["validated_duration_sec"]
            )
            if data.get(
                "validated_duration_sec"
            ) is not None
            else None
        ),
        validations=[
            validation_from_mapping(
                item
            )
            for item in data.get(
                "validations",
                []
            )
        ],
    )