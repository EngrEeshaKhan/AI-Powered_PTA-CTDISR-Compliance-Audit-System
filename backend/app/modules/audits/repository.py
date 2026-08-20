from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules.audits.models import Audit


PROJECT_ROOT = Path(__file__).resolve().parents[4]

STORAGE_DIR = PROJECT_ROOT / "storage" / "audits"
STORAGE_FILE = STORAGE_DIR / "audits.json"


class AuditRepository:

    def __init__(self) -> None:
        STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not STORAGE_FILE.exists():
            self._save([])

    # =========================================================
    # LOAD
    # =========================================================

    def _load(self) -> list[dict[str, Any]]:

        try:

            with STORAGE_FILE.open(
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

            raise ValueError(
                "Audit storage must contain a JSON list."
            )

        return data

    # =========================================================
    # SAVE
    # =========================================================

    def _save(
        self,
        data: list[dict[str, Any]],
    ) -> None:

        temporary_file = (
            STORAGE_FILE.with_suffix(".tmp")
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
            STORAGE_FILE
        )

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        audit: Audit,
    ) -> Audit:

        data = self._load()

        if any(
            item.get("audit_id") == audit.audit_id
            for item in data
        ):

            raise ValueError(
                f"Audit '{audit.audit_id}' already exists."
            )

        data.append(
            audit.to_dict()
        )

        self._save(data)

        return audit

    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(self) -> list[Audit]:

        return [
            Audit(**item)
            for item in self._load()
        ]

    # =========================================================
    # GET ONE
    # =========================================================

    def get_by_id(
        self,
        audit_id: str,
    ) -> Audit | None:

        for item in self._load():

            if item.get("audit_id") == audit_id:

                return Audit(**item)

        return None

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        audit: Audit,
    ) -> Audit | None:

        data = self._load()

        for index, item in enumerate(data):

            if item.get("audit_id") != audit.audit_id:
                continue

            data[index] = audit.to_dict()

            self._save(data)

            return audit

        return None