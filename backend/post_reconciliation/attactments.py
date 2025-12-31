import pandas as pd
from typing import Dict


def build_attachments(
    recon_result: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    Build Attachment-1 and Attachment-2 from reconciliation result.
    """

    delivery_recon = recon_result["delivery_recon"]
    rto_recon = recon_result["rto_recon"]

    # --------------------------------------------------
    # Attachment 1:
    # Delivery present but NOT in RTO
    # --------------------------------------------------
    attachment_1 = delivery_recon[
        delivery_recon["status"] == "Not Matched"
    ].copy()

    # --------------------------------------------------
    # Attachment 2:
    # RTO present but NOT in Delivery (current + previous)
    # --------------------------------------------------
    attachment_2_cols = ["office_name_rto","chassis_no_rto","vin_rto","registration_no_rto","owner_name_rto"]
    attachment_2 = rto_recon[
        (
        (rto_recon['rto_code'] == "UP32") |
        (rto_recon['rto_code'] == "25BH") |
        (rto_recon['rto_code'] == "NEW") 
        )
        &
        (rto_recon["status"] == "Not Matched")
    ].copy()
    attachment_2 = attachment_2[attachment_2_cols]
    # attachment_2.rename()

    return {
        "attachment_1": attachment_1,
        "attachment_2": attachment_2,
    }
