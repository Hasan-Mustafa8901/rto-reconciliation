import pandas as pd
from typing import Optional, Dict


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
        how="left",
    )

    rto_current["status"] = "Matched"
    rto_current.loc[rto_current["vin_del"].isna(), "status"] = "Not Matched"

    # --------------------------------------------------
    # 2. Join Previous Delivery ONLY for unmatched RTO
    # --------------------------------------------------
    if delivery_prev_df is not None:
        rto_prev = pd.merge(
            left=rto_current,
            right=delivery_prev_df,
            left_on="vin_rto",
            right_on="vin_prev",
            how="left",
        )

        mask_prev = (rto_prev["status"] == "Not Matched") & (
            rto_prev["vin_prev"].notna()
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
    delivery_recon.loc[delivery_recon["vin_rto"].isna(), "status"] = "Not Matched"

    # --------------------------------------------------
    # 4. Return both perspectives
    # --------------------------------------------------
    return {
        "rto_recon": rto_recon,
        "delivery_recon": delivery_recon,
    }
