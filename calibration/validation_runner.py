"""
Automatic validation runner.

Runs one motion during the recommended duration,
asks the operator for the measured physical result,
computes the corrected duration and optionally
updates the configuration.
"""

from __future__ import annotations

from core.config import (
    motion_configuration,
    robot_configuration,
)

from core.statistics import (
    compute_statistics,
)

from core.storage import (
    motion_trials,
    set_recommended_duration,
)

from ros.motion_executor import (
    MotionRequest,
    run_motion,
)


# =============================================================================
# INTERNAL
# =============================================================================


def build_request(
    motion_name: str,
    duration_sec: float,
) -> MotionRequest:

    robot = robot_configuration()

    motion = motion_configuration(
        motion_name
    )

    return MotionRequest(

        command_topic=robot["command_topic"],

        linear_x=motion["linear_x"],

        angular_z=motion["angular_z"],

        publish_rate_hz=robot["publish_rate_hz"],

        countdown_sec=robot["countdown_sec"],

        stop_command_count=robot["stop_command_count"],

        maximum_duration_sec=robot["maximum_duration_sec"],

        stop_mode="duration",

        duration_sec=duration_sec,
    )


def target_value(
    motion_name: str,
) -> tuple[str, float]:

    motion = motion_configuration(
        motion_name
    )

    if "target_distance_m" in motion:

        return (
            "distance",
            motion["target_distance_m"],
        )

    return (
        "angle",
        motion["target_angle_deg"],
    )


# =============================================================================
# PUBLIC
# =============================================================================


def validate_motion(
    motion_name: str,
):

    trials = motion_trials(
        motion_name
    )

    if len(trials) < 3:

        print()

        print(
            "At least three trials are required."
        )

        return

    stats = compute_statistics(
        trials
    )

    duration = (
        stats.recommended_duration
    )

    print()

    print("=" * 64)

    print("VALIDATION")

    print("=" * 64)

    print()

    print(
        f"Motion              : {motion_name}"
    )

    print(
        f"Duration            : {duration:.6f} s"
    )

    print()

    request = build_request(
        motion_name,
        duration,
    )

    run_motion(
        request
    )

    mode, target = target_value(
        motion_name
    )

    if mode == "distance":

        measured = float(
            input(
                "\nMeasured distance (m): "
            )
        )

    else:

        measured = float(
            input(
                "\nMeasured angle (deg): "
            )
        )

    corrected_duration = (

        duration

        * target

        / measured

    )

    print()

    print(
        f"Target              : {target:.3f}"
    )

    print(
        f"Measured            : {measured:.3f}"
    )

    print(
        f"Correction factor   : "
        f"{target/measured:.5f}"
    )

    print()

    print(
        f"Old duration        : "
        f"{duration:.6f} s"
    )

    print(
        f"New duration        : "
        f"{corrected_duration:.6f} s"
    )

    print()

    answer = input(
        "Accept correction (y/n)? "
    )

    if answer.lower() != "y":

        print()

        print(
            "Duration unchanged."
        )

        return

    set_recommended_duration(

        motion_name,

        corrected_duration,

    )

    print()

    print(
        "Duration updated."
    )

    print()