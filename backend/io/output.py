import pandas as pd
from pathlib import Path


def write_reconciliation_workbook(
    *,
    output_path: str | Path,
    delivery_recon: pd.DataFrame,
    rto_recon: pd.DataFrame,
    # rto_summary: pd.DataFrame,
    # reconciliation_summary: pd.DataFrame,
):
    """
    Writes the final reconciliation workbook with all required sheets.
    """

    output_path = Path(output_path)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # --------------------------------------------------
        # Attachment 1: Delivery not in RTO
        # --------------------------------------------------
        attachment_1 = delivery_recon[
            delivery_recon["status"] == "Not Matched"
        ]

        attachment_1.to_excel(
            writer,
            sheet_name="Attachment 1",
            index=False
        )

        # --------------------------------------------------
        # Attachment 2: RTO not in Delivery
        # --------------------------------------------------
        attachment_2 = rto_recon[
            # ((rto_recon['rto_code'] == "UP32") |
            # (rto_recon['rto_code'] == "25BH") |
            # (rto_recon['rto_code'] == "NEW") ) &
            (rto_recon["status"] == "Not Matched")
        ]

        attachment_2.to_excel(
            writer,
            sheet_name="Attachment 2",
            index=False
        )

        # --------------------------------------------------
        # RTO Summary
        # --------------------------------------------------
        # rto_summary.to_excel(
        #     writer,
        #     sheet_name="RTO Summary",
        #     index=False
        # )

        # --------------------------------------------------
        # Matched RTO Sheet
        # --------------------------------------------------

        # # --------------------------------------------------
        # # Reconciliation Summary
        # # --------------------------------------------------
        # reconciliation_summary.to_excel(
        #     writer,
        #     sheet_name="Reconciliation_Summary",
        #     index=False
        # )

    return output_path
