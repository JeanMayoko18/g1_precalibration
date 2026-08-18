"""
ROS 2 motion execution for G1 pre-calibration.
"""

from __future__ import annotations

import select
import time
from typing import TextIO

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

from core.models import (
    MotionRequest,
    MotionResult,
)


# =============================================================================
# INPUT
# =============================================================================


def validate_request(
    request: MotionRequest,
) -> MotionRequest:
    """
    Input:
        Motion execution request.

    Processing:
        Validates topic, timing, stop mode, and optional fixed duration.

    Output:
        Validated MotionRequest.

    Used by:
        MotionExecutor.execute().
    """
    if not request.command_topic.startswith(
        "/"
    ):
        raise ValueError(
            "command_topic must be an absolute ROS topic."
        )

    if request.publish_rate_hz <= 0.0:
        raise ValueError(
            "publish_rate_hz must be greater than zero."
        )

    if request.countdown_sec < 0:
        raise ValueError(
            "countdown_sec must be non-negative."
        )

    if request.stop_command_count < 1:
        raise ValueError(
            "stop_command_count must be at least one."
        )

    if request.maximum_duration_sec <= 0.0:
        raise ValueError(
            "maximum_duration_sec must be greater than zero."
        )

    if request.stop_mode not in {
        "operator",
        "duration",
    }:
        raise ValueError(
            "stop_mode must be 'operator' or 'duration'."
        )

    if request.stop_mode == "duration":
        if (
            request.duration_sec is None
            or request.duration_sec <= 0.0
        ):
            raise ValueError(
                "A positive duration_sec is required "
                "for duration stop mode."
            )

        if (
            request.duration_sec
            > request.maximum_duration_sec
        ):
            raise ValueError(
                "duration_sec cannot exceed maximum_duration_sec."
            )

    return request


# =============================================================================
# PROCESSING
# =============================================================================


def build_motion_message(
    request: MotionRequest,
) -> Twist:
    """
    Input:
        Validated motion request.

    Processing:
        Builds the active Twist command.

    Output:
        Twist message containing the configured linear and angular velocity.

    Used by:
        MotionExecutor.__init__().
    """
    message = Twist()

    message.linear.x = float(
        request.linear_x
    )

    message.angular.z = float(
        request.angular_z
    )

    return message


def build_stop_message() -> Twist:
    """
    Input:
        None.

    Processing:
        Creates a Twist message with every component equal to zero.

    Output:
        Zero-velocity Twist message.

    Used by:
        MotionExecutor.publish_stop().
    """
    return Twist()


def run_countdown(
    seconds: int,
) -> None:
    """
    Input:
        Countdown duration.

    Processing:
        Displays one value per second before motion starts.

    Output:
        None.

    Used by:
        MotionExecutor.execute().
    """
    for remaining in range(
        seconds,
        0,
        -1,
    ):
        print(
            f"Starting in {remaining}..."
        )

        time.sleep(
            1.0
        )


def terminal_enter_pressed(
    terminal: TextIO,
) -> bool:
    """
    Input:
        Open controlling terminal.

    Processing:
        Checks non-blockingly whether ENTER was pressed.

    Output:
        True when one terminal line is available.

    Used by:
        MotionExecutor._operator_stop_requested().
    """
    readable, _, _ = select.select(
        [terminal],
        [],
        [],
        0.0,
    )

    if not readable:
        return False

    terminal.readline()

    return True


# =============================================================================
# OUTPUT
# =============================================================================


class MotionExecutor(Node):
    """
    Publish one Twist command until the requested stop condition is reached.
    """

    def __init__(
        self,
        request: MotionRequest,
    ) -> None:
        super().__init__(
            "g1_precalibration_motion_executor"
        )

        self.request = validate_request(
            request
        )

        self.publisher = self.create_publisher(
            Twist,
            self.request.command_topic,
            10,
        )

        self.motion_message = build_motion_message(
            self.request
        )

        self.stop_message = build_stop_message()

    def publish_stop(
        self,
    ) -> None:
        """
        Input:
            Stop publication configuration stored in the request.

        Processing:
            Publishes repeated zero Twist messages at the configured rate.

        Output:
            None.

        Used by:
            execute().
        """
        period_sec = (
            1.0
            / self.request.publish_rate_hz
        )

        for _ in range(
            self.request.stop_command_count
        ):
            self.publisher.publish(
                self.stop_message
            )

            rclpy.spin_once(
                self,
                timeout_sec=0.0,
            )

            time.sleep(
                period_sec
            )

    def _operator_stop_requested(
        self,
        terminal: TextIO,
    ) -> bool:
        """
        Input:
            Controlling terminal.

        Processing:
            Tests whether the operator pressed ENTER.

        Output:
            Stop decision.

        Used by:
            execute().
        """
        return terminal_enter_pressed(
            terminal
        )

    def _duration_stop_reached(
        self,
        elapsed_sec: float,
    ) -> bool:
        """
        Input:
            Current elapsed execution time.

        Processing:
            Compares elapsed time with the requested fixed duration.

        Output:
            True when the fixed duration has been reached.

        Used by:
            execute().
        """
        if self.request.duration_sec is None:
            return False

        return (
            elapsed_sec
            >= self.request.duration_sec
        )

    def execute(
        self,
    ) -> MotionResult:
        """
        Input:
            MotionRequest stored by the executor.

        Processing:
            1. Runs the countdown.
            2. Publishes Twist at the requested fixed rate.
            3. Stops on operator ENTER, fixed duration, timeout, or ROS stop.
            4. Publishes repeated zero commands in every exit path.

        Output:
            MotionResult containing elapsed time, publication count,
            and stop reason.

        Used by:
            CalibrationRunner.
        """
        run_countdown(
            self.request.countdown_sec
        )

        publication_count = 0
        stop_reason = "ros_shutdown"

        period_sec = (
            1.0
            / self.request.publish_rate_hz
        )

        start_time = time.monotonic()
        next_publication_time = start_time

        try:
            with open(
                "/dev/tty",
                "r",
                encoding="utf-8",
                buffering=1,
            ) as terminal:
                print(
                    f"[RUNNING] {self.request.label}"
                )

                if self.request.stop_mode == "operator":
                    print(
                        "Press ENTER when the physical target is reached."
                    )
                else:
                    print(
                        "The motion will stop automatically after "
                        f"{self.request.duration_sec:.6f} s."
                    )

                while rclpy.ok():
                    now = time.monotonic()

                    elapsed_sec = (
                        now
                        - start_time
                    )

                    if (
                        self.request.stop_mode
                        == "operator"
                        and self._operator_stop_requested(
                            terminal
                        )
                    ):
                        stop_reason = "operator"

                        break

                    if (
                        self.request.stop_mode
                        == "duration"
                        and self._duration_stop_reached(
                            elapsed_sec
                        )
                    ):
                        stop_reason = "duration"

                        break

                    if (
                        elapsed_sec
                        >= self.request.maximum_duration_sec
                    ):
                        stop_reason = "safety_timeout"

                        break

                    if now < next_publication_time:
                        time.sleep(
                            min(
                                next_publication_time - now,
                                period_sec,
                            )
                        )

                        continue

                    self.publisher.publish(
                        self.motion_message
                    )

                    rclpy.spin_once(
                        self,
                        timeout_sec=0.0,
                    )

                    publication_count += 1

                    next_publication_time += (
                        period_sec
                    )

        except KeyboardInterrupt:
            stop_reason = "keyboard_interrupt"

        finally:
            elapsed_sec = (
                time.monotonic()
                - start_time
            )

            self.publish_stop()

        return MotionResult(
            elapsed_sec=float(
                elapsed_sec
            ),
            publication_count=int(
                publication_count
            ),
            stop_reason=stop_reason,
        )


# =============================================================================
# ORCHESTRATION
# =============================================================================


def execute_motion(
    request: MotionRequest,
) -> MotionResult:
    """
    Input:
        Complete motion request.

    Processing:
        Creates one temporary MotionExecutor node, executes the motion,
        and destroys the node.

    Output:
        MotionResult.

    Used by:
        CalibrationRunner.

    Preconditions:
        rclpy.init() must already have been called by the application.
    """
    executor = MotionExecutor(
        request
    )

    try:
        return executor.execute()

    finally:
        executor.destroy_node()