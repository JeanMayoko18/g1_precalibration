"""
Pure statistical computations for G1 pre-calibration trials.
"""

from __future__ import annotations

from math import sqrt
from statistics import mean, median, stdev
from typing import Sequence

from .models import StatisticsResult


# =============================================================================
# INPUT
# =============================================================================


def normalize_durations(
    durations: Sequence[float],
) -> list[float]:
    """
    Input:
        Recorded motion durations.

    Processing:
        Converts every value to float and rejects empty, non-positive,
        or non-finite values.

    Output:
        Validated duration list.

    Used by:
        compute_statistics().
    """
    values = [
        float(value)
        for value in durations
    ]

    if not values:
        raise ValueError(
            "At least one trial duration is required."
        )

    for index, value in enumerate(
        values
    ):
        if value <= 0.0:
            raise ValueError(
                f"Duration at index {index} must be greater than zero."
            )

        if not (
            float("-inf")
            < value
            < float("inf")
        ):
            raise ValueError(
                f"Duration at index {index} must be finite."
            )

    return values


# =============================================================================
# PROCESSING
# =============================================================================


def calculate_standard_deviation(
    values: Sequence[float],
) -> float:
    """
    Input:
        Validated duration values.

    Processing:
        Calculates the sample standard deviation when at least two
        observations are available.

    Output:
        Sample standard deviation in seconds.

    Used by:
        compute_statistics().
    """
    if len(
        values
    ) < 2:
        return 0.0

    return float(
        stdev(
            values
        )
    )


def calculate_confidence95_half_width(
    sample_count: int,
    standard_deviation_sec: float,
) -> float:
    """
    Input:
        Number of trials and sample standard deviation.

    Processing:
        Calculates an approximate 95 percent confidence interval
        half-width using 1.96 * sigma / sqrt(n).

    Output:
        Approximate confidence interval half-width in seconds.

    Used by:
        compute_statistics().
    """
    if sample_count < 2:
        return 0.0

    return float(
        1.96
        * standard_deviation_sec
        / sqrt(
            sample_count
        )
    )


def calculate_coefficient_variation(
    mean_sec: float,
    standard_deviation_sec: float,
) -> float:
    """
    Input:
        Mean duration and sample standard deviation.

    Processing:
        Calculates the relative dispersion as a percentage.

    Output:
        Coefficient of variation in percent.

    Used by:
        compute_statistics().
    """
    if mean_sec <= 0.0:
        return 0.0

    return float(
        standard_deviation_sec
        / mean_sec
        * 100.0
    )


def classify_quality(
    coefficient_variation_percent: float,
) -> str:
    """
    Input:
        Coefficient of variation.

    Processing:
        Classifies trial repeatability using fixed project thresholds.

    Output:
        Human-readable repeatability level.

    Used by:
        compute_statistics().
    """
    if coefficient_variation_percent < 1.0:
        return "excellent"

    if coefficient_variation_percent < 3.0:
        return "acceptable"

    return "repeat_required"


# =============================================================================
# OUTPUT
# =============================================================================


def compute_statistics(
    durations: Sequence[float],
) -> StatisticsResult:
    """
    Input:
        Recorded trial durations.

    Processing:
        Calculates central tendency, dispersion, repeatability,
        confidence interval, and the robust candidate duration.

    Output:
        Complete StatisticsResult.

    Used by:
        CalibrationRunner,
        Report.
    """
    values = normalize_durations(
        durations
    )

    sample_count = len(
        values
    )

    mean_sec = float(
        mean(
            values
        )
    )

    median_sec = float(
        median(
            values
        )
    )

    standard_deviation_sec = calculate_standard_deviation(
        values
    )

    coefficient_variation_percent = (
        calculate_coefficient_variation(
            mean_sec,
            standard_deviation_sec,
        )
    )

    confidence95_half_width_sec = (
        calculate_confidence95_half_width(
            sample_count,
            standard_deviation_sec,
        )
    )

    return StatisticsResult(
        sample_count=sample_count,
        minimum_sec=float(
            min(
                values
            )
        ),
        maximum_sec=float(
            max(
                values
            )
        ),
        mean_sec=mean_sec,
        median_sec=median_sec,
        standard_deviation_sec=standard_deviation_sec,
        coefficient_variation_percent=(
            coefficient_variation_percent
        ),
        confidence95_half_width_sec=(
            confidence95_half_width_sec
        ),
        recommended_duration_sec=median_sec,
        quality_level=classify_quality(
            coefficient_variation_percent
        ),
    )