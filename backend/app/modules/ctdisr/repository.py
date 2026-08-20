from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]

CTDISR_STORAGE_DIR = (
    PROJECT_ROOT
    / "storage"
    / "ctdisr"
)

CONTROLS_FILE = (
    CTDISR_STORAGE_DIR
    / "controls.json"
)


class CTDISRControlRepository:

    def __init__(self) -> None:

        CTDISR_STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not CONTROLS_FILE.exists():
            self._write_data([])

    # =========================================================
    # INTERNAL
    # =========================================================

    def _read_data(self) -> list[dict[str, Any]]:

        try:

            with CONTROLS_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return []

        if not isinstance(data, list):
            return []

        return data

    def _write_data(
        self,
        data: list[dict[str, Any]],
    ) -> None:

        temporary_file = (
            CONTROLS_FILE.with_suffix(".tmp")
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temporary_file.replace(
            CONTROLS_FILE
        )

    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(
        self,
        include_inactive: bool = False,
    ) -> list[dict[str, Any]]:

        controls = self._read_data()

        if include_inactive:
            return controls

        return [
            control
            for control in controls
            if control.get(
                "status",
                "active",
            ) == "active"
        ]

    # =========================================================
    # GET ONE
    # =========================================================

    def get_by_id(
        self,
        control_id: str,
    ) -> dict[str, Any] | None:

        controls = self._read_data()

        for control in controls:

            if (
                control.get("control_id")
                == control_id
            ):
                return control

        return None

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        control: dict[str, Any],
    ) -> dict[str, Any]:

        controls = self._read_data()

        controls.append(control)

        self._write_data(controls)

        return control

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        control_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:

        controls = self._read_data()

        for index, control in enumerate(
            controls
        ):

            if (
                control.get("control_id")
                != control_id
            ):
                continue

            control.update(updates)

            controls[index] = control

            self._write_data(controls)

            return control

        return None

    # =========================================================
    # DEACTIVATE
    # =========================================================

    def deactivate(
        self,
        control_id: str,
    ) -> dict[str, Any] | None:

        return self.update(
            control_id,
            {
                "status": "inactive",
            },
        )

    # =========================================================
    # COUNT
    # =========================================================

    def count(
        self,
        include_inactive: bool = False,
    ) -> int:

        return len(
            self.get_all(
                include_inactive=include_inactive
            )
        )