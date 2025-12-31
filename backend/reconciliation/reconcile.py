import pandas as pd
from typing import Optional, Dict

# def reconcile_bidirectional(
#     *,
#     rto_df: pd.DataFrame,
#     delivery_df: pd.DataFrame,
#     delivery_prev_df: Optional[pd.DataFrame] = None,
# ) -> Dict[str, pd.DataFrame]:
#     """
#     Bidirectional reconciliation.

#     - Attachment-1: Delivery → RTO
#     - Attachment-2: RTO → (Delivery + Previous Delivery)
#     """

#     # =============================
#     # Build identifier sets
#     # =============================
#     rto_chassis = set(rto_df["chassis_no"].dropna())
#     rto_vins = set(rto_df["vin"].dropna())

#     delivery_chassis = set(delivery_df["chassis_no"].dropna())
#     delivery_vins = set(delivery_df["vin"].dropna())
    
#     prev_chassis = set()
#     prev_vins = set()

#     if delivery_prev_df is not None:
#         prev_chassis = set(delivery_prev_df["chassis_no"].dropna())
#         prev_vins = set(delivery_prev_df["vin"].dropna())

#     # =============================
#     # DELIVERY → RTO (Attachment-1)
#     # =============================
#     delivery_recon = delivery_df.copy()
#     delivery_recon["status"] = None

#     # Match on chassis
#     mask = delivery_recon["chassis_no"].isin(rto_chassis)
#     delivery_recon.loc[mask, "status"] = "MATCHED_CHASSIS"

#     # Match on VIN (fallback)
#     mask = (
#         delivery_recon["status"].isna()
#         & delivery_recon["vin"].isin(rto_vins)
#     )
#     delivery_recon.loc[mask, "status"] = "MATCHED_VIN"

#     # Missing in RTO
#     delivery_recon.loc[
#         delivery_recon["status"].isna(),
#         "status"
#     ] = "MISSING_IN_RTO"

#     # =============================
#     # RTO → DELIVERY (Attachment-2)
#     # =============================
#     rto_recon = rto_df.copy()
#     rto_recon["status"] = None

#     # Match with CURRENT delivery on chassis
#     mask = rto_recon["chassis_no"].isin(delivery_chassis)
#     rto_recon.loc[mask, "status"] = "MATCHED_CURRENT_DELIVERY"

#     # Match with CURRENT delivery on VIN
#     mask = (
#         rto_recon["status"].isna()
#         & rto_recon["vin"].isin(delivery_vins)
#     )
#     rto_recon.loc[mask, "status"] = "MATCHED_CURRENT_DELIVERY"

#     # Match with PREVIOUS delivery on chassis
#     mask = (
#         rto_recon["status"].isna()
#         & rto_recon["chassis_no"].isin(prev_chassis)
#     )
#     rto_recon.loc[mask, "status"] = "MATCHED_PREVIOUS_DELIVERY"

#     # Match with PREVIOUS delivery on VIN
#     mask = (
#         rto_recon["status"].isna()
#         & rto_recon["vin"].isin(prev_vins)
#     )
#     rto_recon.loc[mask, "status"] = "MATCHED_PREVIOUS_DELIVERY"

#     # Truly missing in delivery
#     rto_recon.loc[
#         rto_recon["status"].isna(),
#         "status"
#     ] = "MISSING_IN_DELIVERY"

#     # =============================
#     # Return both attachments
#     # =============================
#     return {
#         "delivery_recon": delivery_recon,  # Attachment-1
#         "rto_recon": rto_recon,             # Attachment-2
#     }


def reconcile_delivery_rto(
    *,
    rto_df: pd.DataFrame,
    delivery_df: pd.DataFrame,
    delivery_prev_df: Optional[pd.DataFrame] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Join-based reconciliation.
    This mirrors the tested notebook logic.
    """

    # --------------------------------------------------
    # 1. RTO ⟵ LEFT JOIN ⟶ Current Delivery
    # --------------------------------------------------
    rto_current = pd.merge(
        left=rto_df,
        right=delivery_df,
        left_on="vin_rto",
        right_on="vin_del",
        how="left"
    )

    rto_current["status"] = "Matched"
    rto_current.loc[
        rto_current["vin_del"].isna(),
        "status"
    ] = "Not Matched"

    # --------------------------------------------------
    # 2. Join Previous Delivery ONLY for unmatched RTO
    # --------------------------------------------------
    if delivery_prev_df is not None:
        rto_prev = pd.merge(
            left = rto_current,
            right=delivery_prev_df,
            left_on='vin_rto',
            right_on='vin_prev',
            how="left"
        )

        mask_prev = (
            (rto_prev["status"] == "Not Matched")
            & (rto_prev["vin_prev"].notna())
        )

        rto_prev.loc[mask_prev, "status"] = "Matched (Previous)"

        rto_recon = rto_prev
    else:
        rto_recon = rto_current

    # --------------------------------------------------
    # 3. DELIVERY ⟵ LEFT JOIN ⟶ RTO
    # --------------------------------------------------
    delivery_recon = pd.merge(
        left=delivery_df,
        right=rto_df,
        left_on="vin_del",
        right_on="vin_rto",
        how="left",
    )

    delivery_recon["status"] = "Matched"
    delivery_recon.loc[
        delivery_recon["vin_rto"].isna(),
        "status"
    ] = "Not Matched"

    # --------------------------------------------------
    # 4. Return both perspectives
    # --------------------------------------------------
    return {
        "rto_recon": rto_recon,
        "delivery_recon": delivery_recon,
    }
