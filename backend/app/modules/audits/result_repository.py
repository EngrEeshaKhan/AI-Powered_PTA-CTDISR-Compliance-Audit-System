from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules.audits.result_models import AuditResult


PROJECT_ROOT = Path(__file__).resolve().parents[4]

STORAGE_DIR = PROJECT_ROOT / "storage" / "audits"
STORAGE_FILE = STORAGE_DIR / "audit_results.json"


class AuditResultRepository:

    def __init__(self) -> None:
        STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not STORAGE_FILE.exists():
            self._save([])

    # =========================================================
    # INTERNAL LOAD
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
            return []

        return data

    # =========================================================
    # INTERNAL SAVE
    # =========================================================

    def _save(
        self,
        data: list[dict[str, Any]],
    ) -> None:

        temporary_file = STORAGE_FILE.with_suffix(".tmp")

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

        temporary_file.replace(STORAGE_FILE)

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        result: AuditResult,
    ) -> AuditResult:

        data = self._load()

        if any(
            item.get("result_id") == result.result_id
            for item in data
        ):
            raise ValueError(
                f"Audit result '{result.result_id}' already exists."
            )

        data.append(result.to_dict())

        self._save(data)

        return result

    # =========================================================
    # GET ALL RESULTS
    # =========================================================

    def get_all(self) -> list[AuditResult]:

        return [
            AuditResult(**item)
            for item in self._load()
        ]

    # =========================================================
    # GET RESULTS FOR ONE AUDIT
    # =========================================================

    def get_by_audit(
        self,
        audit_id: str,
    ) -> list[AuditResult]:

        return [
            AuditResult(**item)
            for item in self._load()
            if item.get("audit_id") == audit_id
        ]

    # =========================================================
    # GET ONE RESULT
    # =========================================================

    def get_by_id(
        self,
        result_id: str,
    ) -> AuditResult | None:

        for item in self._load():

            if item.get("result_id") == result_id:
                return AuditResult(**item)

        return None

    # =========================================================
    # GET RESULT FOR AUDIT + CONTROL
    # =========================================================

    def get_by_audit_and_control(
        self,
        audit_id: str,
        control_id: str,
    ) -> AuditResult | None:

        for item in self._load():

            if (
                item.get("audit_id") == audit_id
                and item.get("control_id") == control_id
            ):
                return AuditResult(**item)

        return None

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        result_id: str,
        updates: dict[str, Any],
    ) -> AuditResult | None:

        data = self._load()

        for index, item in enumerate(data):

            if item.get("result_id") != result_id:
                continue

            item.update(updates)

            data[index] = item

            self._save(data)

            return AuditResult(**item)

        return None

    # =========================================================
    # DELETE
    # =========================================================

    def delete(
        self,
        result_id: str,
    ) -> bool:

        data = self._load()

        new_data = [
            item
            for item in data
            if item.get("result_id") != result_id
        ]

        if len(new_data) == len(data):
            return False

        self._save(new_data)

        return True