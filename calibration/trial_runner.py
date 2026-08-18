"""
Generic pre-calibration trial runner.
"""

from __future__ import annotations

from core.config import (
    motion_configuration,
    robot_configuration,
)

from core.storage import (
    add_trial,
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
) -> MotionRequest:
    """
    Build a MotionRequest from the configuration.
    """

    robot = robot_configuration()

    motion = motion_configuration(
        motion_name
    )

    return MotionRequest(

        command_topic=robot[
            "command_topic"
        ],

        linear_x=motion[
            "linear_x"
        ],

        angular_z=motion[
            "angular_z"
        ],

        publish_rate_hz=robot[
            "publish_rate_hz"
        ],

        countdown_sec=robot[
            "countdown_sec"
        ],

        stop_command_count=robot[
            "stop_command_count"
        ],

        maximum_duration_sec=robot[
            "maximum_duration_sec"
        ],

        stop_mode="operator",

        duration_sec=None,
    )


# =============================================================================
# PUBLIC
# =============================================================================


def run_trial(
    motion_name: str,
):
    """
    Execute one operator-controlled trial.
    """

    request = build_request(
        motion_name
    )

    result = run_motion(
        request
    )

    add_trial(
        motion_name,
        result.elapsed_sec,
    )

    print()

    print("=" * 64)

    print("TRIAL COMPLETED")

    print("=" * 64)

    print()

    print(
        f"Motion            : {motion_name}"
    )

    print(
        f"Duration          : "
        f"{result.elapsed_sec:.6f} s"
    )

    print(
        f"Publications      : "
        f"{result.publication_count}"
    )

    print(
        f"Stop reason       : "
        f"{result.stop_reason}"
    )

    print()

    return result