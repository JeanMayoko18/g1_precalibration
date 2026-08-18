"""
Utilities to clear stored pre-calibration results.
"""

from __future__ import annotations

from core.storage import (
    clear_all,
    clear_motion,
)


# =============================================================================
# CONSTANTS
# =============================================================================

MOTIONS = {

    "1": "straight_4m",

    "2": "straight_2m",

    "3": "rotate_left",

    "4": "rotate_right",

}


# =============================================================================
# INTERNAL
# =============================================================================


def _print_motion_menu() -> None:

    print()

    print("=" * 64)

    print("CLEAR ONE MOTION")

    print("=" * 64)

    print()

    print("1) Straight 4 m")

    print("2) Straight 2 m")

    print("3) Rotate Left 90°")

    print("4) Rotate Right 90°")

    print()

    print("0) Cancel")

    print()


# =============================================================================
# PUBLIC
# =============================================================================


def clear_single_motion() -> None:

    _print_motion_menu()

    choice = input(
        "Choice > "
    ).strip()

    if choice == "0":

        return

    if choice not in MOTIONS:

        print()

        print(
            "Invalid selection."
        )

        return

    motion = MOTIONS[
        choice
    ]

    answer = input(
        f"Delete all trials for '{motion}' (y/n)? "
    )

    if answer.lower() != "y":

        print()

        print(
            "Operation cancelled."
        )

        return

    clear_motion(
        motion
    )

    print()

    print(
        "Trials deleted."
    )

    print()


def clear_everything() -> None:

    print()

    answer = input(
        "Delete ALL stored trials (y/n)? "
    )

    if answer.lower() != "y":

        print()

        print(
            "Operation cancelled."
        )

        return

    clear_all()

    print()

    print(
        "All stored trials deleted."
    )

    print()