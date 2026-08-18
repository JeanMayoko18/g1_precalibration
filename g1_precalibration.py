#!/usr/bin/env python3
"""
Entry point for the G1 pre-calibration application.
"""

from __future__ import annotations

import sys

import rclpy

from application import Application


# =============================================================================
# ORCHESTRATION
# =============================================================================


def main() -> int:
    """
    Initialize ROS, run the application, and shut ROS down safely.
    """
    rclpy.init()

    try:
        application = Application()
        application.run()

        return 0

    except KeyboardInterrupt:
        print(
            "\n[INTERRUPTED] Application stopped by operator."
        )

        return 130

    except Exception as exc:
        print(
            f"\n[ERROR] {exc}",
            file=sys.stderr,
        )

        return 1

    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(
        main()
    )