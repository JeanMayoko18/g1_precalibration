"""
Pre-calibration trial and physical validation orchestration.
"""

from __future__ import annotations

from core.config import Configuration
from core.models import (
    MotionConfiguration,
    MotionRequest,
    MotionResult,
    StatisticsResult,
    TrialResult,
    ValidationPreparation,
    ValidationResult,
)
from core.statistics import compute_statistics
from core.storage import Storage
from ros.motion_executor import execute_motion


# =============================================================================
# INPUT
# =============================================================================


def validate_measured_value(
    measured_value: float,
) -> float:
    """
    Input:
        Physical distance or angle measured by the operator.

    Processing:
        Converts the value to float and verifies that it is finite and
        strictly positive.

    Output:
        Validated physical measurement.

    Used by:
        CalibrationRunner.finalize_validation().
    """
    value = float(
        measured_value
    )

    if not (
        float("-inf")
        < value
        < float("inf")
    ):
        raise ValueError(
            "The measured value must be finite."
        )

    if value <= 0.0:
        raise ValueError(
            "The measured value must be greater than zero."
        )

    return value


# =============================================================================
# PROCESSING
# =============================================================================


def build_motion_request(
    *,
    robot,
    motion: MotionConfiguration,
    stop_mode: str,
    duration_sec: float | None,
) -> MotionRequest:
    """
    Input:
        Robot configuration, motion configuration, stop mode,
        and optional fixed duration.

    Processing:
        Combines configuration data into one complete ROS motion request.

    Output:
        MotionRequest ready for the ROS executor.

    Used by:
        CalibrationRunner.run_trial(),
        CalibrationRunner.prepare_validation().
    """
    return MotionRequest(
        motion_name=motion.name,
        label=motion.label,
        command_topic=robot.command_topic,
        linear_x=motion.linear_x,
        angular_z=motion.angular_z,
        publish_rate_hz=robot.publish_rate_hz,
        countdown_sec=robot.countdown_sec,
        stop_command_count=robot.stop_command_count,
        maximum_duration_sec=(
            robot.maximum_duration_sec
        ),
        stop_mode=stop_mode,
        duration_sec=duration_sec,
    )


def calculate_corrected_duration(
    *,
    candidate_duration_sec: float,
    target_value: float,
    measured_value: float,
) -> tuple[float, float]:
    """
    Input:
        Candidate command duration, physical target, and measured result.

    Processing:
        Calculates the proportional correction factor:

            correction = target / measured

        and applies it to the candidate duration.

    Output:
        Correction factor and corrected duration.

    Used by:
        CalibrationRunner.finalize_validation().
    """
    correction_factor = (
        target_value
        / measured_value
    )

    corrected_duration_sec = (
        candidate_duration_sec
        * correction_factor
    )

    return (
        float(
            correction_factor
        ),
        float(
            corrected_duration_sec
        ),
    )


# =============================================================================
# OUTPUT
# =============================================================================


class CalibrationRunner:
    """
    Coordinate configuration, ROS motion execution, statistics, and storage.

    This class contains no console input or display logic.
    """

    def __init__(
        self,
        configuration: Configuration,
        storage: Storage,
    ) -> None:
        self.configuration = configuration
        self.storage = storage

    def statistics(
        self,
        motion_name: str,
    ) -> StatisticsResult:
        """
        Input:
            Motion identifier.

        Processing:
            Reads all recorded durations and calculates their statistics.

        Output:
            StatisticsResult.

        Used by:
            run_trial(),
            prepare_validation(),
            reporting.
        """
        return compute_statistics(
            self.storage.durations(
                motion_name
            )
        )

    def candidate_duration(
        self,
        motion_name: str,
        statistics: StatisticsResult,
    ) -> float:
        """
        Input:
            Motion identifier and current trial statistics.

        Processing:
            Reuses the latest accepted duration when one exists.
            Otherwise, uses the robust median recommendation.

        Output:
            Duration to test during physical validation.

        Used by:
            prepare_validation().
        """
        validated_duration = (
            self.storage.validated_duration(
                motion_name
            )
        )

        if validated_duration is not None:
            return float(
                validated_duration
            )

        return float(
            statistics.recommended_duration_sec
        )

    # =========================================================================
    # TRIAL
    # =========================================================================

    def run_trial(
        self,
        motion_name: str,
    ) -> TrialResult:
        """
        Input:
            Configured motion identifier.

        Processing:
            1. Builds an operator-controlled MotionRequest.
            2. Executes the ROS motion.
            3. Stores the measured duration and execution metadata.
            4. Recalculates repeatability statistics.
            5. Saves a timestamped history snapshot.

        Output:
            Complete TrialResult.

        Used by:
            Application menu actions 1 to 4.

        Side effects:
            Moves the robot and writes YAML results/history.
        """
        motion = self.configuration.motion(
            motion_name
        )

        request = build_motion_request(
            robot=self.configuration.robot,
            motion=motion,
            stop_mode="operator",
            duration_sec=None,
        )

        motion_result = execute_motion(
            request
        )

        self.storage.add_trial(
            motion_name,
            motion_result,
        )

        statistics = self.statistics(
            motion_name
        )

        self.storage.save_history_snapshot(
            f"{motion_name}_trial"
        )

        return TrialResult(
            motion=motion,
            motion_result=motion_result,
            statistics=statistics,
        )

    # =========================================================================
    # VALIDATION PREPARATION
    # =========================================================================

    def prepare_validation(
        self,
        motion_name: str,
        minimum_trial_count: int = 3,
    ) -> ValidationPreparation:
        """
        Input:
            Motion identifier and minimum required number of trials.

        Processing:
            1. Verifies that enough operator-controlled trials exist.
            2. Calculates current statistics.
            3. Selects the current candidate duration.
            4. Builds a fixed-duration MotionRequest.

        Output:
            ValidationPreparation.

        Used by:
            Application validation workflow.
        """
        durations = self.storage.durations(
            motion_name
        )

        if len(
            durations
        ) < minimum_trial_count:
            raise RuntimeError(
                "At least "
                f"{minimum_trial_count} trials are required "
                f"for '{motion_name}'."
            )

        motion = self.configuration.motion(
            motion_name
        )

        statistics = compute_statistics(
            durations
        )

        candidate_duration_sec = (
            self.candidate_duration(
                motion_name,
                statistics,
            )
        )

        request = build_motion_request(
            robot=self.configuration.robot,
            motion=motion,
            stop_mode="duration",
            duration_sec=candidate_duration_sec,
        )

        return ValidationPreparation(
            motion=motion,
            statistics=statistics,
            candidate_duration_sec=(
                candidate_duration_sec
            ),
            request=request,
        )

    def execute_validation_motion(
        self,
        preparation: ValidationPreparation,
    ) -> MotionResult:
        """
        Input:
            Prepared fixed-duration validation.

        Processing:
            Executes the robot motion using the candidate duration.

        Output:
            MotionResult from the ROS executor.

        Used by:
            Application before asking for the physical measurement.

        Side effects:
            Moves the robot.
        """
        return execute_motion(
            preparation.request
        )

    # =========================================================================
    # VALIDATION FINALIZATION
    # =========================================================================

    def finalize_validation(
        self,
        preparation: ValidationPreparation,
        *,
        measured_value: float,
        accepted: bool,
    ) -> ValidationResult:
        """
        Input:
            Validation preparation, physical measurement, and operator
            acceptance decision.

        Processing:
            1. Validates the physical measurement.
            2. Calculates the proportional correction.
            3. Stores the complete validation attempt.
            4. Updates the official validated duration only when accepted.
            5. Saves a timestamped history snapshot.

        Output:
            Complete ValidationResult.

        Used by:
            Application validation workflow.

        Side effects:
            Writes YAML results/history.
        """
        measured = validate_measured_value(
            measured_value
        )

        motion = preparation.motion

        correction_factor, corrected_duration_sec = (
            calculate_corrected_duration(
                candidate_duration_sec=(
                    preparation.candidate_duration_sec
                ),
                target_value=motion.target_value,
                measured_value=measured,
            )
        )

        self.storage.add_validation(
            motion.name,
            candidate_duration_sec=(
                preparation.candidate_duration_sec
            ),
            target_value=motion.target_value,
            measured_value=measured,
            target_unit=motion.target_unit,
            correction_factor=correction_factor,
            corrected_duration_sec=(
                corrected_duration_sec
            ),
            accepted=accepted,
        )

        self.storage.save_history_snapshot(
            f"{motion.name}_validation"
        )

        return ValidationResult(
            motion=motion,
            candidate_duration_sec=(
                preparation.candidate_duration_sec
            ),
            target_value=motion.target_value,
            measured_value=measured,
            target_unit=motion.target_unit,
            correction_factor=correction_factor,
            corrected_duration_sec=(
                corrected_duration_sec
            ),
            accepted=accepted,
        )