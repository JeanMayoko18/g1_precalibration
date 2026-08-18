"""
Export recommended durations to YAML.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.config import (
    load_configuration,
)

from core.storage import (
    recommended_duration,
)


# =============================================================================
# EXPORT
# =============================================================================


def export_yaml(
    output_path: Path,
) -> None:
    """
    Export the validated calibration values.
    """

    configuration = load_configuration()

    motions = configuration[
        "motions"
    ]

    export = {

        "robot": configuration[
            "robot"
        ],

        "motions": {},

    }

    for motion_name in motions:

        motion = dict(
            motions[
                motion_name
            ]
        )

        motion[
            "recommended_duration_sec"
        ] = recommended_duration(
            motion_name
        )

        export[
            "motions"
        ][
            motion_name
        ] = motion

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        yaml.safe_dump(

            export,

            file,

            sort_keys=False,

            allow_unicode=True,

        )

    print()

    print("=" * 64)

    print("EXPORT COMPLETED")

    print("=" * 64)

    print()

    print(
        f"File : {output_path}"
    )

    print()