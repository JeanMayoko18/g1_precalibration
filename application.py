"""
Main application orchestration for the G1 pre-calibration tool.
"""

from __future__ import annotations

from pathlib import Path

from calibration.runner import CalibrationRunner

from core.config import Configuration

from core.menu import (
    confirm,
    get_choice,
    pause,
    read_positive_float,
)

from core.statistics import compute_statistics

from core.storage import Storage

from reports.report import (
    build_motion_report,
    export_validated_durations,
    show_all_motion_reports,
    show_motion_result,
    show_trial_result,
    show_validation_preparation,
    show_validation_result,
)


# =============================================================================
# APPLICATION
# =============================================================================


class Application:
    """
    Main application controller.
    """

    def __init__(
        self,
    ) -> None:

        self.configuration = Configuration()

        self.storage = Storage(
            self.configuration
        )

        self.runner = CalibrationRunner(
            self.configuration,
            self.storage,
        )

    # =========================================================================
    # INTERNAL
    # =========================================================================

    @staticmethod
    def motion_from_trial_choice(
        choice: str,
    ) -> str:

        return {

            "1": "straight_4m",

            "2": "straight_2m",

            "3": "rotate_left",

            "4": "rotate_right",

        }[choice]

    @staticmethod
    def motion_from_validation_choice(
        choice: str,
    ) -> str:

        return {

            "5": "straight_4m",

            "6": "straight_2m",

            "7": "rotate_left",

            "8": "rotate_right",

        }[choice]

    # =========================================================================
    # TRIAL
    # =========================================================================

    def run_trial(
        self,
        motion_name: str,
    ) -> None:

        result = self.runner.run_trial(
            motion_name
        )

        show_trial_result(
            result
        )

        pause()

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def run_validation(
        self,
        motion_name: str,
    ) -> None:

        preparation = (
            self.runner.prepare_validation(
                motion_name
            )
        )

        show_validation_preparation(
            preparation
        )

        if not confirm(
            "Start validation motion?"
        ):
            return

        motion_result = (
            self.runner.execute_validation_motion(
                preparation
            )
        )

        show_motion_result(
            motion_result
        )

        measured_value = (
            read_positive_float(
                f"Measured "
                f"{preparation.motion.target_unit}: "
            )
        )

        accepted = confirm(
            "Accept corrected duration?"
        )

        result = (
            self.runner.finalize_validation(
                preparation,
                measured_value=measured_value,
                accepted=accepted,
            )
        )

        show_validation_result(
            result
        )

        pause()

    # =========================================================================
    # REPORTS
    # =========================================================================

    def show_reports(
        self,
    ) -> None:

        reports = []

        for motion in (
            self.configuration.motions()
        ):

            durations = (
                self.storage.durations(
                    motion.name
                )
            )

            statistics = None

            if durations:

                statistics = (
                    compute_statistics(
                        durations
                    )
                )

            reports.append(

                build_motion_report(

                    motion,

                    self.storage.state(
                        motion.name
                    ),

                    statistics,

                )

            )

        show_all_motion_reports(
            reports
        )

        pause()

    # =========================================================================
    # EXPORT
    # =========================================================================

    def export(
        self,
    ) -> None:

        output = (

            Path.cwd()

            / "validated_durations.yaml"

        )

        export_validated_durations(

            self.configuration,

            self.storage,

            output,

        )

        pause()

    # =========================================================================
    # DELETE
    # =========================================================================

    def clear_motion(
        self,
    ) -> None:

        print()

        print("Available motions:")

        for motion in (
            self.configuration.motions()
        ):

            print(
                f"  - {motion.name}"
            )

        print()

        motion_name = input(
            "Motion name: "
        ).strip()

        if motion_name not in (
            self.configuration.motion_names()
        ):

            print(
                "Unknown motion."
            )

            pause()

            return

        if confirm(
            "Delete all trials?"
        ):

            self.storage.clear_motion(
                motion_name
            )

        pause()

    def clear_all(
        self,
    ) -> None:

        if confirm(
            "Delete every stored result?"
        ):

            self.storage.clear_all()

        pause()

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    def run(
        self,
    ) -> None:

        while True:

            choice = get_choice()

            if choice == "0":

                break

            elif choice in {
                "1",
                "2",
                "3",
                "4",
            }:

                self.run_trial(

                    self.motion_from_trial_choice(
                        choice
                    )

                )

            elif choice in {
                "5",
                "6",
                "7",
                "8",
            }:

                self.run_validation(

                    self.motion_from_validation_choice(
                        choice
                    )

                )

            elif choice == "9":

                self.show_reports()

            elif choice == "10":

                self.export()

            elif choice == "11":

                self.clear_motion()

            elif choice == "12":

                self.clear_all()