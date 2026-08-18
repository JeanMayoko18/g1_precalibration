"""
Statistics report generation.
"""

from __future__ import annotations

from core.statistics import (
    compute_statistics,
)

from core.storage import (
    motion_trials,
)


# =============================================================================
# INTERNAL
# =============================================================================


def print_header() -> None:

    print()

    print("=" * 72)

    print("G1 PRE-CALIBRATION STATISTICS")

    print("=" * 72)


def print_motion_header(
    motion_name: str,
) -> None:

    print()

    print("-" * 72)

    print(
        motion_name.upper()
    )

    print("-" * 72)


# =============================================================================
# REPORT
# =============================================================================


def show_statistics() -> None:

    print_header()

    motions = [

        "straight_4m",

        "straight_2m",

        "rotate_left",

        "rotate_right",

    ]

    for motion in motions:

        trials = motion_trials(
            motion
        )

        print_motion_header(
            motion
        )

        if not trials:

            print()

            print(
                "No recorded trials."
            )

            continue

        statistics = compute_statistics(
            trials
        )

        print()

        for index, value in enumerate(

            sorted(trials),

            start=1,

        ):

            print(
                f"{index:2d}. "
                f"{value:.6f} s"
            )

        print()

        print(
            f"Trials                 : {statistics.sample_count}"
        )

        print(
            f"Minimum                : {statistics.minimum:.6f} s"
        )

        print(
            f"Maximum                : {statistics.maximum:.6f} s"
        )

        print(
            f"Mean                   : {statistics.mean:.6f} s"
        )

        print(
            f"Median                 : {statistics.median:.6f} s"
        )

        print(
            "Standard deviation     : "
            f"{statistics.standard_deviation:.6f} s"
        )

        print(
            "Coefficient variation  : "
            f"{statistics.coefficient_variation_percent:.2f} %"
        )

        print(
            "95% confidence         : "
            f"±{statistics.confidence95_half_width:.6f} s"
        )

        print()

        print(
            "Recommended duration   : "
            f"{statistics.recommended_duration:.6f} s"
        )

    print()

    input(
        "Press ENTER..."
    )