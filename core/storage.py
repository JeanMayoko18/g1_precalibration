"""
Persistent storage management for G1 pre-calibration results.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import (
    Configuration,
    load_yaml,
    save_yaml,
)
from .models import (
    MotionResult,
    MotionState,
    Trial,
    Validation,
    motion_state_from_mapping,
    motion_state_to_mapping,
)


# =============================================================================
# STORAGE
# =============================================================================


class Storage:
    """
    Keep all pre-calibration results in memory and persist every modification.
    """

    def __init__(
        self,
        configuration: Configuration,
    ) -> None:
        self.configuration = configuration
        self.path = configuration.results_path.resolve()

        self._states = self._load_states()

    # =========================================================================
    # INPUT
    # =========================================================================

    def _load_states(
        self,
    ) -> dict[str, MotionState]:
        """
        Load every configured motion state from the results YAML file.
        """
        raw_data = load_yaml(
            self.path
        )

        states: dict[
            str,
            MotionState,
        ] = {}

        for motion_name in self.configuration.motion_names():
            motion_data = raw_data.get(
                motion_name,
                {},
            )

            if not isinstance(
                motion_data,
                dict,
            ):
                raise RuntimeError(
                    f"Stored result '{motion_name}' must be a mapping."
                )

            states[motion_name] = motion_state_from_mapping(
                motion_name,
                motion_data,
            )

        return states

    # =========================================================================
    # PROCESSING
    # =========================================================================

    def _next_trial_id(
        self,
        motion_name: str,
    ) -> int:
        """
        Calculate the next persistent trial identifier.
        """
        trials = self.state(
            motion_name
        ).trials

        if not trials:
            return 1

        return max(
            trial.id
            for trial in trials
        ) + 1

    def _serialize(
        self,
    ) -> dict[str, Any]:
        """
        Convert every in-memory motion state to a YAML-compatible mapping.
        """
        return {
            motion_name: motion_state_to_mapping(
                state
            )
            for motion_name, state in self._states.items()
        }

    # =========================================================================
    # OUTPUT
    # =========================================================================

    def save(
        self,
    ) -> None:
        """
        Persist all in-memory states.
        """
        save_yaml(
            self.path,
            self._serialize(),
        )

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Return an independent serialized copy of all stored data.
        """
        return deepcopy(
            self._serialize()
        )

    # =========================================================================
    # READ
    # =========================================================================

    def state(
        self,
        motion_name: str,
    ) -> MotionState:
        """
        Return the in-memory state associated with one motion.
        """
        try:
            return self._states[
                motion_name
            ]
        except KeyError as exc:
            raise KeyError(
                f"Unknown motion state: {motion_name}"
            ) from exc

    def states(
        self,
    ) -> tuple[
        MotionState,
        ...,
    ]:
        """
        Return every in-memory motion state.
        """
        return tuple(
            self._states.values()
        )

    def trials(
        self,
        motion_name: str,
    ) -> tuple[
        Trial,
        ...,
    ]:
        """
        Return every recorded trial for one motion.
        """
        return tuple(
            self.state(
                motion_name
            ).trials
        )

    def durations(
        self,
        motion_name: str,
    ) -> list[float]:
        """
        Return only the recorded trial durations for one motion.
        """
        return [
            trial.duration_sec
            for trial in self.state(
                motion_name
            ).trials
        ]

    def validated_duration(
        self,
        motion_name: str,
    ) -> float | None:
        """
        Return the accepted fixed duration for one motion.
        """
        return self.state(
            motion_name
        ).validated_duration_sec

    def validations(
        self,
        motion_name: str,
    ) -> tuple[
        Validation,
        ...,
    ]:
        """
        Return every validation attempt for one motion.
        """
        return tuple(
            self.state(
                motion_name
            ).validations
        )

    # =========================================================================
    # TRIAL WRITE
    # =========================================================================

    def add_trial(
        self,
        motion_name: str,
        motion_result: MotionResult,
    ) -> Trial:
        """
        Create, store, and persist one operator-controlled trial.
        """
        trial = Trial(
            id=self._next_trial_id(
                motion_name
            ),
            timestamp=datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            duration_sec=float(
                motion_result.elapsed_sec
            ),
            publication_count=int(
                motion_result.publication_count
            ),
            stop_reason=str(
                motion_result.stop_reason
            ),
        )

        self.state(
            motion_name
        ).trials.append(
            trial
        )

        self.save()

        return trial

    # =========================================================================
    # VALIDATION WRITE
    # =========================================================================

    def add_validation(
        self,
        motion_name: str,
        *,
        candidate_duration_sec: float,
        target_value: float,
        measured_value: float,
        target_unit: str,
        correction_factor: float,
        corrected_duration_sec: float,
        accepted: bool,
    ) -> Validation:
        """
        Store one physical validation and update the accepted duration.
        """
        validation = Validation(
            timestamp=datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            candidate_duration_sec=float(
                candidate_duration_sec
            ),
            target_value=float(
                target_value
            ),
            measured_value=float(
                measured_value
            ),
            target_unit=str(
                target_unit
            ),
            correction_factor=float(
                correction_factor
            ),
            corrected_duration_sec=float(
                corrected_duration_sec
            ),
            accepted=bool(
                accepted
            ),
        )

        state = self.state(
            motion_name
        )

        state.validations.append(
            validation
        )

        if accepted:
            state.validated_duration_sec = float(
                corrected_duration_sec
            )

        self.save()

        return validation

    # =========================================================================
    # DELETE
    # =========================================================================

    def remove_trial(
        self,
        motion_name: str,
        trial_id: int,
    ) -> bool:
        """
        Delete one trial using its persistent identifier.
        """
        state = self.state(
            motion_name
        )

        for index, trial in enumerate(
            state.trials
        ):
            if trial.id == trial_id:
                del state.trials[
                    index
                ]

                self.save()

                return True

        return False

    def clear_motion(
        self,
        motion_name: str,
    ) -> None:
        """
        Remove all trials and validations associated with one motion.
        """
        state = self.state(
            motion_name
        )

        state.trials.clear()
        state.validations.clear()
        state.validated_duration_sec = None

        self.save()

    def clear_all(
        self,
    ) -> None:
        """
        Remove all stored pre-calibration results.
        """
        for state in self._states.values():
            state.trials.clear()
            state.validations.clear()
            state.validated_duration_sec = None

        self.save()

    # =========================================================================
    # HISTORY
    # =========================================================================

    def save_history_snapshot(
        self,
        stem: str,
    ) -> Path:
        """
        Persist a timestamped YAML snapshot in the project history directory.
        """
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        safe_stem = stem.strip().replace(
            " ",
            "_",
        )

        output_path = (
            self.configuration.history_directory
            / f"{timestamp}_{safe_stem}.yaml"
        )

        save_yaml(
            output_path,
            self.snapshot(),
        )

        return output_path