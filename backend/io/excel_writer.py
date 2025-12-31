from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from datetime import datetime


def write_output_workbook(
    *,
    attachments: Dict[str, pd.DataFrame],
    # rto_summary: pd.DataFrame,
    dealership: str,
    output_dir: Optional[str] = None,
) -> str:
    """
    Writes final reconciliation output to an Excel workbook.
    Returns output file path.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"RTO_Reconciliation_{dealership}_{timestamp}.xlsx"

    output_path = (
        Path(output_dir) / filename
        if output_dir
        else Path(filename)
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        # Attachments
        attachments["attachment_1"].to_excel(
            writer,
            sheet_name="Attachment 1",
            index=False,
        )

        attachments["attachment_2"].to_excel(
            writer,
            sheet_name="Attachment 2",
            index=False,
        )

        # # Summary
        # rto_summary.to_excel(
        #     writer,
        #     sheet_name="RTO Summary",
        #     index=True,
        # )

    return str(output_path)
