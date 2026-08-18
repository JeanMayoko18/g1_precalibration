"""
Console reporting and YAML export for G1 pre-calibration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.config import (
    Configuration,
    save_yaml,
)
from core.models import (
    MotionConfiguration,
    MotionReport,
    MotionResult,
    StatisticsResult,
    TrialResult,
    ValidationPreparation,
    ValidationResult,
)
from core.storage import Storage


# =============================================================================
# CONSTANTS
# =============================================================================


SEPARATOR_WIDTH = 72


# =============================================================================
# GENERIC OUTPUT
# =============================================================================


def print_separator(
    character: str = "=",
) -> None:
    """
    Input:
        Separator character.

    Processing:
        Builds one fixed-width console separator.

    Output:
        Prints the separator.

    Used by:
        All report display functions.
    """
    print(
        character
        * SEPARATOR_WIDTH
    )


def print_title(
    title: str,
) -> None:
    """
    Input:
        Console section title.

    Processing:
        Surrounds the title with separators.

    Output:
        Prints a formatted title.

    Used by:
        All high-level report display functions.
    """
    print()

    print_separator()

    print(
        title
    )

    print_separator()

    print()


def format_optional_duration(
    value: float | None,
) -> str:
    """
    Input:
        Optional duration.

    Processing:
        Formats an existing duration or returns a placeholder.

    Output:
        Human-readable duration.

    Used by:
        show_motion_report(),
        export_validated_durations().
    """
    if value is None:
        return "Not validated"

    return (
        f"{value:.6f} s"
    )


# =============================================================================
# MOTION CONFIGURATION
# =============================================================================

def build_motion_report(
    motion: MotionConfiguration,
    state,
    statistics: StatisticsResult | None,
) -> MotionReport:
    """
    Assemble one complete motion report from precomputed data.
    """
    return MotionReport(
        motion=motion,
        state=state,
        statistics=statistics,
    )

def show_motion_configuration(
    motion: MotionConfiguration,
) -> None:
    """
    Input:
        Motion configuration.

    Processing:
        Formats the command and physical target.

    Output:
        Prints the motion configuration.

    Used by:
        Application before trials and validations.
    """
    print(
        f"Motion                  : {motion.label}"
    )

    print(
        f"Linear velocity         : {motion.linear_x:+.3f} m/s"
    )

    print(
        f"Angular velocity        : {motion.angular_z:+.3f} rad/s"
    )

    print(
        f"Physical target         : "
        f"{motion.target_value:.3f} {motion.target_unit}"
    )


# =============================================================================
# STATISTICS
# =============================================================================


def show_statistics(
    statistics: StatisticsResult,
) -> None:
    """
    Input:
        Precomputed statistics.

    Processing:
        Formats central tendency, dispersion, confidence,
        recommendation, and repeatability quality.

    Output:
        Prints the statistics.

    Used by:
        show_trial_result(),
        show_validation_preparation(),
        show_motion_report().
    """
    print(
        f"Trial count             : {statistics.sample_count}"
    )

    print(
        f"Minimum                 : {statistics.minimum_sec:.6f} s"
    )

    print(
        f"Maximum                 : {statistics.maximum_sec:.6f} s"
    )

    print(
        f"Mean                    : {statistics.mean_sec:.6f} s"
    )

    print(
        f"Median                  : {statistics.median_sec:.6f} s"
    )

    print(
        "Standard deviation      : "
        f"{statistics.standard_deviation_sec:.6f} s"
    )

    print(
        "Coefficient of variation: "
        f"{statistics.coefficient_variation_percent:.2f} %"
    )

    print(
        "Approximate 95% CI      : "
        f"±{statistics.confidence95_half_width_sec:.6f} s"
    )

    print(
        "Recommended duration    : "
        f"{statistics.recommended_duration_sec:.6f} s"
    )

    print(
        f"Repeatability quality   : {statistics.quality_level}"
    )


# =============================================================================
# TRIAL RESULT
# =============================================================================


def show_trial_result(
    result: TrialResult,
) -> None:
    """
    Input:
        Complete trial workflow result.

    Processing:
        Formats the motion execution result and updated statistics.

    Output:
        Prints the trial report.

    Used by:
        Application after menu actions 1 to 4.
    """
    print_title(
        "PRE-CALIBRATION TRIAL COMPLETED"
    )

    show_motion_configuration(
        result.motion
    )

    print()

    print(
        "Measured duration       : "
        f"{result.motion_result.elapsed_sec:.6f} s"
    )

    print(
        "Published commands      : "
        f"{result.motion_result.publication_count}"
    )

    print(
        "Stop reason             : "
        f"{result.motion_result.stop_reason}"
    )

    print()

    show_statistics(
        result.statistics
    )

    print()


# =============================================================================
# VALIDATION PREPARATION
# =============================================================================


def show_validation_preparation(
    preparation: ValidationPreparation,
) -> None:
    """
    Input:
        Prepared fixed-duration validation.

    Processing:
        Formats the candidate duration and current statistics.

    Output:
        Prints the validation plan before robot motion.

    Used by:
        Application before executing a validation motion.
    """
    print_title(
        "PHYSICAL VALIDATION"
    )

    show_motion_configuration(
        preparation.motion
    )

    print()

    show_statistics(
        preparation.statistics
    )

    print()

    print(
        "Candidate duration      : "
        f"{preparation.candidate_duration_sec:.6f} s"
    )

    print(
        "Stop mode               : automatic fixed duration"
    )

    print()


# =============================================================================
# MOTION EXECUTION RESULT
# =============================================================================


def show_motion_result(
    result: MotionResult,
) -> None:
    """
    Input:
        ROS motion execution result.

    Processing:
        Formats execution duration, publication count, and stop reason.

    Output:
        Prints the motion execution result.

    Used by:
        Application after a fixed-duration validation motion.
    """
    print()

    print_separator(
        "-"
    )

    print(
        "MOTION EXECUTION RESULT"
    )

    print_separator(
        "-"
    )

    print()

    print(
        f"Actual duration         : {result.elapsed_sec:.6f} s"
    )

    print(
        f"Published commands      : {result.publication_count}"
    )

    print(
        f"Stop reason             : {result.stop_reason}"
    )

    print()


# =============================================================================
# VALIDATION RESULT
# =============================================================================


def show_validation_result(
    result: ValidationResult,
) -> None:
    """
    Input:
        Final physical validation result.

    Processing:
        Formats target, measured value, correction, and accepted duration.

    Output:
        Prints the validation result.

    Used by:
        Application after validation finalization.
    """
    print_title(
        "VALIDATION RESULT"
    )

    show_motion_configuration(
        result.motion
    )

    print()

    print(
        f"Candidate duration      : "
        f"{result.candidate_duration_sec:.6f} s"
    )

    print(
        f"Target                  : "
        f"{result.target_value:.6f} {result.target_unit}"
    )

    print(
        f"Measured                : "
        f"{result.measured_value:.6f} {result.target_unit}"
    )

    print(
        f"Correction factor       : "
        f"{result.correction_factor:.9f}"
    )

    print(
        f"Corrected duration      : "
        f"{result.corrected_duration_sec:.6f} s"
    )

    print(
        "Status                  : "
        + (
            "ACCEPTED"
            if result.accepted
            else "REJECTED"
        )
    )

    print()


# =============================================================================
# COMPLETE MOTION REPORT
# =============================================================================


def show_motion_report(
    report: MotionReport,
) -> None:
    """
    Input:
        Complete motion report assembled by the application.

    Processing:
        Formats trials, statistics, validation history,
        and official duration.

    Output:
        Prints one complete motion report.

    Used by:
        show_all_motion_reports().
    """
    print_title(
        report.motion.label.upper()
    )

    show_motion_configuration(
        report.motion
    )

    print()

    if not report.state.trials:
        print(
            "No trial has been recorded."
        )

    else:
        print(
            "Recorded trials"
        )

        print_separator(
            "-"
        )

        for trial in report.state.trials:
            print(
                f"  Trial {trial.id:03d}"
                f" | {trial.duration_sec:.6f} s"
                f" | {trial.stop_reason}"
                f" | {trial.timestamp}"
            )

    print()

    if report.statistics is not None:
        show_statistics(
            report.statistics
        )

    else:
        print(
            "Statistics              : Not available"
        )

    print()

    print(
        "Validated duration       : "
        f"{format_optional_duration(report.state.validated_duration_sec)}"
    )

    print(
        "Validation attempts      : "
        f"{len(report.state.validations)}"
    )

    if report.state.validations:
        print()

        print(
            "Validation history"
        )

        print_separator(
            "-"
        )

        for index, validation in enumerate(
            report.state.validations,
            start=1,
        ):
            status = (
                "accepted"
                if validation.accepted
                else "rejected"
            )

            print(
                f"  Validation {index:03d}"
                f" | measured={validation.measured_value:.6f}"
                f" {validation.target_unit}"
                f" | duration={validation.corrected_duration_sec:.6f} s"
                f" | {status}"
                f" | {validation.timestamp}"
            )

    print()


def show_all_motion_reports(
    reports: Iterable[MotionReport],
) -> None:
    """
    Input:
        Complete reports for all configured motions.

    Processing:
        Displays each report in the supplied order.

    Output:
        Prints all motion reports.

    Used by:
        Application menu action 9.
    """
    report_list = list(
        reports
    )

    if not report_list:
        print_title(
            "PRE-CALIBRATION REPORT"
        )

        print(
            "No configured motion is available."
        )

        return

    for report in report_list:
        show_motion_report(
            report
        )


# =============================================================================
# YAML EXPORT
# =============================================================================


def build_validated_duration_export(
    configuration: Configuration,
    storage: Storage,
) -> dict:
    """
    Input:
        Application configuration and persistent storage.

    Processing:
        Combines robot settings, motion commands, targets,
        and validated durations into one reusable mapping.

    Output:
        YAML-compatible export mapping.

    Used by:
        export_validated_durations().
    """
    motions: dict = {}

    for motion in configuration.motions():
        motions[
            motion.name
        ] = {
            "label": motion.label,
            "linear_x": motion.linear_x,
            "angular_z": motion.angular_z,
            "target_type": motion.target_type,
            "target_value": motion.target_value,
            "target_unit": motion.target_unit,
            "validated_duration_sec": (
                storage.validated_duration(
                    motion.name
                )
            ),
        }

    robot = configuration.robot

    return {
        "robot": {
            "command_topic": robot.command_topic,
            "publish_rate_hz": robot.publish_rate_hz,
            "countdown_sec": robot.countdown_sec,
            "stop_command_count": (
                robot.stop_command_count
            ),
            "maximum_duration_sec": (
                robot.maximum_duration_sec
            ),
        },
        "motions": motions,
    }


def export_validated_durations(
    configuration: Configuration,
    storage: Storage,
    output_path: Path,
) -> Path:
    """
    Input:
        Configuration, storage, and destination path.

    Processing:
        Builds and writes the complete validated-duration export.

    Output:
        Resolved output path.

    Used by:
        Application menu action 10.

    Side effects:
        Writes one YAML file.
    """
    output = output_path.resolve()

    save_yaml(
        output,
        build_validated_duration_export(
            configuration,
            storage,
        ),
    )

    print_title(
        "VALIDATED DURATIONS EXPORTED"
    )

    print(
        f"Output file            : {output}"
    )

    print()

    return output