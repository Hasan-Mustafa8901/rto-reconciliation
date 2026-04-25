import pandas as pd
from typing import Dict


def build_attachments(recon_result: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Build Attachment-1 and Attachment-2 from reconciliation result.
    """

    delivery_recon = recon_result["delivery_recon"]
    rto_recon = recon_result["rto_recon"]

    # --------------------------------------------------
    # Attachment 1:
    # Delivery present but NOT in RTO
    # --------------------------------------------------
    attachment_1_cols = [
        "showroom_del",
        "delivery_date_del",
        "customer_name_del",
        "chassis_no_del",
        "vin_del",
        "status",
    ]
    attachment_1 = (
        delivery_recon[delivery_recon["status"] == "Not Matched"]
        .sort_values(by=["showroom_del", "delivery_date_del"], na_position="last")
        .reset_index(drop=True)
        .copy()
    )

    attachment_1["delivery_date_del"] = pd.to_datetime(
        attachment_1["delivery_date_del"], format="%Y-%m-%d"
    ).dt.strftime("%d-%m-%Y")

    attachment_1 = attachment_1[attachment_1_cols]

    attachment_1.rename(
        {
            "showroom_del": "Showroom",
            "delivery_date_del": "Delivery Date",
            "customer_name_del": "Customer Name",
            "chassis_no_del": "Chassis Number",
            "vin_del": "VIN Number",
            "status": "RTO Status",
        },
        axis=1,
        inplace=True,
    )

    # --------------------------------------------------
    # Attachment 2:
    # RTO present but NOT in Delivery (current + previous)
    # --------------------------------------------------
    attachment_2_cols = [
        "office_name_rto",
        "chassis_no_rto",
        "vin_rto",
        "registration_no_rto",
        "owner_name_rto",
        "status",
    ]
    attachment_2 = rto_recon[
        (
            (rto_recon["rto_code"] == "UP32")
            | (rto_recon["rto_code"] == "25BH")
            | (rto_recon["rto_code"] == "NEW")
        )
        & (rto_recon["status"] == "Not Matched")
    ].copy()
    attachment_2 = attachment_2[attachment_2_cols]
    attachment_2.rename(
        {
            "office_name_rto": "Location",
            "chassis_no_rto": "Chassis Number",
            "vin_rto": "VIN Number",
            "registration_no_rto": "Registration Number",
            "owner_name_rto": "Owner Name",
            "status": "Status",
        },
        axis=1,
        inplace=True,
    )

    return {
        "attachment_1": attachment_1,
        "attachment_2": attachment_2,
        "delivery_reco": delivery_recon,
        "rto_reco": rto_recon,
    }
