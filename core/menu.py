"""
Console menu for the G1 pre-calibration application.
"""

from __future__ import annotations


# =============================================================================
# CONSTANTS
# =============================================================================


MENU_WIDTH = 72

VALID_CHOICES = {
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
}


# =============================================================================
# OUTPUT
# =============================================================================


def print_separator(
    character: str = "=",
) -> None:
    """
    Print one fixed-width separator.
    """
    print(
        character
        * MENU_WIDTH
    )


def print_menu() -> None:
    """
    Display the main application menu.
    """
    print()

    print_separator()

    print(
        "G1 PRE-CALIBRATION TOOL"
    )

    print_separator()

    print()

    print(
        "PRE-CALIBRATION TRIALS"
    )

    print(
        "  1) Straight 4 m"
    )

    print(
        "  2) Straight 2 m"
    )

    print(
        "  3) Rotate Left 90 deg"
    )

    print(
        "  4) Rotate Right 90 deg"
    )

    print()

    print(
        "PHYSICAL VALIDATION"
    )

    print(
        "  5) Validate Straight 4 m"
    )

    print(
        "  6) Validate Straight 2 m"
    )

    print(
        "  7) Validate Rotate Left 90 deg"
    )

    print(
        "  8) Validate Rotate Right 90 deg"
    )

    print()

    print(
        "REPORTS"
    )

    print(
        "  9) Show complete statistics"
    )

    print(
        " 10) Export validated durations"
    )

    print()

    print(
        "DATA MANAGEMENT"
    )

    print(
        " 11) Clear one motion"
    )

    print(
        " 12) Clear all results"
    )

    print()

    print(
        "  0) Quit"
    )

    print()


# =============================================================================
# INPUT
# =============================================================================


def get_choice() -> str:
    """
    Display the menu until the operator enters a valid choice.
    """
    while True:
        print_menu()

        choice = input(
            "Choice > "
        ).strip()

        if choice in VALID_CHOICES:
            return choice

        print()

        print(
            "[ERROR] Invalid menu choice."
        )


def confirm(
    prompt: str,
    *,
    default: bool = False,
) -> bool:
    """
    Ask one yes/no question.

    Empty input returns the configured default.
    """
    suffix = (
        " [Y/n] "
        if default
        else " [y/N] "
    )

    while True:
        answer = input(
            prompt
            + suffix
        ).strip().lower()

        if not answer:
            return default

        if answer in {
            "y",
            "yes",
        }:
            return True

        if answer in {
            "n",
            "no",
        }:
            return False

        print(
            "[ERROR] Enter y or n."
        )


def read_positive_float(
    prompt: str,
) -> float:
    """
    Read one finite strictly positive numeric value.
    """
    while True:
        raw_value = input(
            prompt
        ).strip()

        try:
            value = float(
                raw_value
            )

        except ValueError:
            print(
                "[ERROR] Enter a valid number."
            )

            continue

        if not (
            float("-inf")
            < value
            < float("inf")
        ):
            print(
                "[ERROR] The value must be finite."
            )

            continue

        if value <= 0.0:
            print(
                "[ERROR] The value must be greater than zero."
            )

            continue

        return value


def pause() -> None:
    """
    Wait for the operator before returning to the main menu.
    """
    input(
        "\nPress ENTER to continue..."
    )