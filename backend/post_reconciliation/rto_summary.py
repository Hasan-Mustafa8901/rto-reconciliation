import pandas as pd
from typing import List


def total_per_rto(df: pd.DataFrame) -> pd.Series:
    total_rto = df.groupby("rto_code")["status"].count()
    return total_rto


def all_rto(df: pd.DataFrame):
    all = df["rto_code"].unique()
    return list(all)


def rto_x_showroom(df: pd.DataFrame, all_rto_code: List[str]) -> pd.DataFrame:
    result = pd.crosstab(index=df["rto_code"], columns=df["showroom_del"]).reindex(
        all_rto_code, fill_value=0
    )

    return result


def other_cases(df: pd.DataFrame, showrooms: List[str]) -> pd.DataFrame:
    df["out_of_scope"] = df["Total"] - (df[showrooms].sum(axis=1))
    return df


def build_rto_summary(
    *,
    rto_recon: pd.DataFrame,
) -> pd.DataFrame:
    """
    Builds RTO Summary from reconciliation outputs.
    Safe against missing showrooms and previous-month matches.
    """
    # Get the RTO Codes present in the data.
    all_rto_codes = all_rto(rto_recon)

    # Do a crosstab of RTO vs Showroom
    crosstab_showroom_rto = rto_x_showroom(rto_recon, all_rto_code=all_rto_codes)

    # Get the total deliveries for each RTO
    crosstab_showroom_rto["Total"] = total_per_rto(rto_recon)

    showrooms = rto_recon["showroom_del"].dropna().unique().tolist()
    # Get the other case
    crosstab_showroom_rto = other_cases(crosstab_showroom_rto, showrooms=showrooms)

    return crosstab_showroom_rto


# def build_rto_summary(
#     *,
#     rto_recon: pd.DataFrame,
#     delivery_recon: pd.DataFrame,
#     delivery_prev_df: pd.DataFrame | None = None,
# ) -> pd.DataFrame:
#     """
#     Builds RTO Summary from reconciliation outputs.
#     Safe against missing showrooms and previous-month matches.
#     """

#     known_showrooms=list(delivery_recon['showroom_del'].unique())

#     # --------------------------------------------------
#     # 1. Filter only matched RTO records
#     # --------------------------------------------------
#     matched_rto = rto_recon[
#         rto_recon["status"].isin(
#             ["Matched", "Matched (Previous)"]
#         )
#     ].copy()

#     if matched_rto.empty:
#         raise ValueError("No matched RTO records found. Cannot build RTO summary.")

#     # --------------------------------------------------
#     # 2. Build VIN → Showroom lookup
#     #    (current + previous deliveries)
#     # --------------------------------------------------
#     showroom_sources = [delivery_recon[["vin", "showroom"]]]

#     if delivery_prev_df is not None:
#         showroom_sources.append(delivery_prev_df[["vin", "showroom"]])

#     delivery_showroom = (
#         pd.concat(showroom_sources, ignore_index=True)
#         .dropna(subset=["vin", "showroom"])
#         .drop_duplicates(subset=["vin"])
#     )
#     delivery_showroom['vin'] = delivery_showroom["vin"].apply(lambda x: str(x).zfill(6))
#     if delivery_showroom.empty:
#         raise ValueError(
#             "No VIN → Showroom mapping available from delivery data."
#         )
#     matched_rto['vin'] = matched_rto["vin"].astype(str)
#     delivery_showroom['vin'] = delivery_showroom["vin"].astype(str)

#     # --------------------------------------------------
#     # 3. Attach showroom to matched RTO (SAFE MERGE)
#     # --------------------------------------------------
#     matched_rto = matched_rto.merge(
#         delivery_showroom,
#         on="vin",
#         how="left"
#     )

#     # --------------------------------------------------
#     # 4. Defensive check: unresolved showroom mappings
#     # --------------------------------------------------
#     unresolved = matched_rto["showroom"].isna().sum()

#     if unresolved > 0:
#         print(
#             f"WARNING: {unresolved} RTO records could not be mapped to any showroom."
#         )
#     all_codes = matched_rto["rto_code"].unique()
#     # --------------------------------------------------
#     # 5. Crosstab: RTO × Showroom
#     # --------------------------------------------------
#     rto_showroom = pd.crosstab(
#         index=matched_rto["rto_code"],
#         columns=matched_rto["showroom"]
#     ).reindex(all_codes,fill_value=0)

#     # Ensure all known showrooms exist
#     for sr in known_showrooms:
#         if sr not in rto_showroom.columns:
#             rto_showroom[sr] = 0

#     # --------------------------------------------------
#     # 6. Total registrations per RTO
#     # --------------------------------------------------
#     total_rto = matched_rto.groupby("rto_code").size()
#     rto_showroom["Total"] = total_rto

#     # --------------------------------------------------
#     # 7. TR calculation (unchanged logic)
#     # --------------------------------------------------
#     rto_showroom["TR"] = (
#         rto_showroom["Total"]
#         - rto_showroom[known_showrooms].sum(axis=1)
#     )

#     # --------------------------------------------------
#     # 8. Final column ordering
#     # --------------------------------------------------
#     final_cols = known_showrooms + ["Total", "TR"]
#     rto_showroom = rto_showroom[final_cols]

#     return rto_showroom.reset_index()
