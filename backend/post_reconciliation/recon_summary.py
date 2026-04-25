import pandas as pd
from typing import Tuple


def build_reconciliation_summary(
    *,
    delivery_recon: pd.DataFrame,
    rto_recon: pd.DataFrame,
    non_up32_codes: list[str] = ["UP32"],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Builds reconciliation summary tables from reconciled datasets.

    Returns:
    - delivery_summary_df
    - rto_summary_df
    """

    # ======================================================
    # SECTION 1: Reconciliation of Delivery Records vs RTO
    # ======================================================

    total_deliveries = len(delivery_recon)

    total_by_showroom = delivery_recon.groupby("showroom_del").size()

    matched_del = delivery_recon[delivery_recon["status"] == "Matched"]
    matched_by_showroom = matched_del.groupby("showroom_del").size()

    mismatch_del = delivery_recon[delivery_recon["status"] == "Not Matched"]
    mismatch_by_showroom = mismatch_del.groupby("showroom_del").size()

    delivery_summary_rows = []

    # ---- Total Deliveries ----
    delivery_summary_rows.append(
        (
            "Total Deliveries reported to us",
            "",
            total_deliveries,
            "Total entries in delivery data",
        )
    )
    for showroom, count in total_by_showroom.items():
        delivery_summary_rows.append((f"{showroom}", count, ""))

    # ---- Matched ----
    delivery_summary_rows.append(
        (
            "Matched with RTO",
            "",
            matched_del.shape[0],
            "Delivery initimated that found in RTO records.",
        )
    )
    for showroom, count in matched_by_showroom.items():
        delivery_summary_rows.append((f"{showroom}", count, "", ""))

    # ---- Mismatch ----
    delivery_summary_rows.append(
        (
            "Mismatch with RTO (Refer to Attachment-1)",
            "",
            mismatch_del.shape[0],
            "Deliveries intimated but not found in RTO records.",
        )
    )
    for showroom, count in mismatch_by_showroom.items():
        delivery_summary_rows.append((f"{showroom}", count, "", ""))

    delivery_summary_df = pd.DataFrame(
        delivery_summary_rows, columns=["Particulars", "Nos", "Total", "Remarks"]
    )

    # ======================================================
    # SECTION 2: Reconciliation of RTO Records
    # ======================================================

    total_rto = len(rto_recon)

    matched_rto = rto_recon[rto_recon["status"].isin(["Matched"])]

    matched_rto_by_showroom = (
        matched_rto.dropna(subset=["showroom_del"]).groupby("showroom_del").size()
    )

    non_up32 = rto_recon[
        (
            ~rto_recon["rto_code"].isin(non_up32_codes)
        )  # this is quite confusing it is like inverted logic but it works so don't change it.
        & (rto_recon["status"] == "Not Matched")
    ]

    prev_delivery = rto_recon[rto_recon["status"] == "Matched (Previous)"]

    missing_delivery = total_rto - (
        matched_rto.shape[0] + non_up32.shape[0] + prev_delivery.shape[0]
    )

    rto_summary_rows = [
        (
            "Total RTO records reported to us",
            "",
            total_rto,
            "Total records in RTO Data",
        ),
        (
            "Matched with Delivery Records",
            "",
            matched_rto.shape[0],
            "RTO records that matched with deliveries",
        ),
    ]

    for showroom, count in matched_rto_by_showroom.items():
        rto_summary_rows.append((f"{showroom}", count, "", ""))

    rto_summary_rows.extend(
        [
            (
                "Delivered From Territories (Non UP 32 No.)",
                "",
                non_up32.shape[0],
                "RTO Records",
            ),
            ("Delivered Last Month", "", prev_delivery.shape[0], ""),
            ("Final difference (Refer to Attachment-2) ", "", missing_delivery, ""),
        ]
    )

    rto_summary_df = pd.DataFrame(
        rto_summary_rows, columns=["Particulars", "Nos", "Total", "Remarks"]
    )

    return delivery_summary_df, rto_summary_df
