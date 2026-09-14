
from __future__ import annotations

from io import BytesIO
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

from app.modules.audits.json_audit_service import (
    JsonAuditService,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


service = JsonAuditService()


# =========================================================
# GET ALL REPORT DATA
# =========================================================

@router.get(
    "",
)
def get_all_reports():
    """
    Return all saved audit results that can be used
    to generate compliance reports.
    """

    try:
        results = service.get_all()

        return {
            "success": True,
            "count": len(results),
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load report data: {str(exc)}",
        )


# =========================================================
# GET ONE REPORT
# =========================================================

@router.get(
    "/{audit_id}",
)
def get_report(
    audit_id: str,
):
    """
    Return all saved data for one audit report.
    """

    try:
        result = service.get_one(
            audit_id,
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Audit report "
                    f"'{audit_id}' not found."
                ),
            )

        return {
            "success": True,
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load report: {str(exc)}",
        )


# =========================================================
# EXPORT ALL REPORTS TO EXCEL
# =========================================================

@router.get(
    "/export/excel",
    summary="Export all audit reports to Excel",
)
def export_reports_to_excel():
    """
    Generate an Excel file containing all saved audit results.
    """

    try:
        results = service.get_all()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No audit results available for export.",
            )

        # -------------------------------------------------
        # Create workbook
        # -------------------------------------------------

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "PTA Audit Report"

        # -------------------------------------------------
        # Excel columns
        # -------------------------------------------------

        headers = [
            "Audit ID",
            "Control",
            "Control Level",
            "Control Description",
            "Control Interpretation",
            "PTA Response",
            "PTA Recommendations",
            "Action By",
            "NTC Comments",
            "Status",
            "Version",
            "Created At",
            "Updated At",
        ]

        worksheet.append(headers)

        # -------------------------------------------------
        # Header formatting
        # -------------------------------------------------

        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        # -------------------------------------------------
        # Add audit results
        # -------------------------------------------------

        for result in results:
            worksheet.append(
                [
                    result.get("audit_id", ""),
                    result.get("control_id", ""),
                    result.get("control_level", ""),
                    result.get("control_description", ""),
                    result.get("control_interpretation", ""),
                    result.get("pta_response", ""),
                    result.get("pta_recommendations", ""),
                    result.get("action_by", ""),
                    result.get("ntc_comments", ""),
                    result.get("status", ""),
                    result.get("version", ""),
                    result.get("created_at", ""),
                    result.get("updated_at", ""),
                ]
            )

        # -------------------------------------------------
        # Formatting
        # -------------------------------------------------

        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        # Enable wrapping for all data cells
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

        # -------------------------------------------------
        # Set column widths
        # -------------------------------------------------

        column_widths = {
            "A": 38,   # Audit ID
            "B": 12,   # Control
            "C": 15,   # Control Level
            "D": 50,   # Control Description
            "E": 60,   # Control Interpretation
            "F": 60,   # PTA Response
            "G": 60,   # PTA Recommendations
            "H": 25,   # Action By
            "I": 40,   # NTC Comments
            "J": 15,   # Status
            "K": 12,   # Version
            "L": 25,   # Created At
            "M": 25,   # Updated At
        }

        for column, width in column_widths.items():
            worksheet.column_dimensions[column].width = width

        # -------------------------------------------------
        # Set row height
        # -------------------------------------------------

        for row in worksheet.iter_rows():
            row_number = row[0].row

            if row_number == 1:
                worksheet.row_dimensions[row_number].height = 30
            else:
                worksheet.row_dimensions[row_number].height = 90

        # -------------------------------------------------
        # Save workbook to memory
        # -------------------------------------------------

        excel_file = BytesIO()

        workbook.save(excel_file)

        excel_file.seek(0)

        # -------------------------------------------------
        # Return Excel file
        # -------------------------------------------------

        return StreamingResponse(
            excel_file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="PTA_CTDSIR_Audit_Report.xlsx"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate Excel report: {str(exc)}",
        )
