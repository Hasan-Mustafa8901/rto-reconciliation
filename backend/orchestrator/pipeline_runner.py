from pathlib import Path
from typing import Dict, Optional
import traceback
from pandas import DataFrame

# --- Validation ---
from backend.validation.input_schema import (
    validate_workbook,
    load_workbook,
)

# --- Processing ---
from backend.processing.normalize_project import normalize_and_project

# --- Reconciliation ---
from backend.reconciliation.reconcile import reconcile_delivery_rto

# --- Summaries ---
from backend.post_reconciliation.attactments import build_attachments
from backend.post_reconciliation.rto_summary import build_rto_summary
from backend.post_reconciliation.recon_summary import build_reconciliation_summary

# --- Reporting ---
from backend.io.excel_writer import write_output_workbook


class PipelineError(Exception):
    """Raised when the reconciliation pipeline fails."""
    pass

def run_reconciliation_pipeline(
    *,
    input_file_path: str,
    dealership: str,
    output_dir: Optional[str] = None,
) -> Dict[str, object]:
    """
    Orchestrates the complete RTO reconciliation pipeline.

    Returns:
    {
        "success": bool,
        "messages": list[str],
        "output_file": str | None
    }
    """

    messages: list[str] = []

    try:
        # --------------------------------------------------
        # 1. Validate input workbook (PATH-BASED)
        # --------------------------------------------------
        messages.append("Validating input workbook…")
        validation = validate_workbook(str(input_file_path))

        if not validation.is_valid:
            error_messages = "\n".join(
                str(err) for err in validation.errors
            )
            raise PipelineError(
                f"Validation failed:\n{error_messages}"
            )
        # --------------------------------------------------
        # 2. Load workbook
        # --------------------------------------------------
        messages.append("Loading workbook…")
        workbook = load_workbook(str(input_file_path))

        # --------------------------------------------------
        # 3. Normalize & project
        # --------------------------------------------------
        messages.append("Normalizing and projecting data…")
        normalized = normalize_and_project(
            workbook,
            rto_sheet="RTO Data",
            delivery_current_sheet="Delivery Data",
            delivery_previous_sheet="Delivery Data (Previous)",
        )
        # --------------------------------------------------
        # 4. Reconcile
        # --------------------------------------------------
        messages.append("Reconciling RTO and Delivery data…")
        recon_result = reconcile_delivery_rto(
            rto_df=normalized["rto"],
            delivery_df=normalized["delivery_current"],
            delivery_prev_df=normalized.get("delivery_previous"),
        )

        messages.append("Building attachments…")
        attachments = build_attachments(recon_result)

        messages.append("Building RTO summary…")
        rto_summary = build_rto_summary(rto_recon=recon_result["rto_recon"])

        messages.append("Build Reconciliation Summary...")
        recon_summary = build_reconciliation_summary(
                delivery_recon=recon_result["delivery_recon"],
                rto_recon=recon_result["rto_recon"]
            )

        messages.append("Writing output Excel file…")
        output_file = write_output_workbook(
            attachments=attachments,
            rto_summary=rto_summary,
            recon_summary=recon_summary,
            dealership=dealership,
            output_dir=output_dir,
        )

        messages.append("✅ Reconciliation completed successfully.")

        return {
            "success": True,
            "messages": messages,
            "output_file": output_file,
        }
    
    except PipelineError as e:
        return{
            "success": False,
            "messages": [str(e)],
            "output_file": None
        }

    except Exception as e:
        return {
            "success": False,
            "messages": [
                "Unexpected Pipeline failed.",
                str(e),
                traceback.format_exc(),
            ],
            "output_file": None,
        }

