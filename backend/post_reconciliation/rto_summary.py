import pandas as pd
from typing import List
from .map_rto_city import RTO_CITY_MAP


def total_per_rto(df: pd.DataFrame) -> pd.Series:
    total_rto = df.groupby("rto_code")["status"].count()
    return total_rto


def total_vehicles_per_rto(df: pd.DataFrame) -> pd.Series:
    return df.groupby("rto_code").size()


def showroom_total(df: pd.DataFrame, showrooms: List[str]) -> pd.Series:
    valid_showrooms = [s for s in showrooms if s in df.columns]
    return df[valid_showrooms].sum(axis=1)


def all_rto(df: pd.DataFrame):
    all = df["rto_code"].unique()
    return list(all)


def rto_x_showroom(df: pd.DataFrame, all_rto_code: List[str]) -> pd.DataFrame:
    result = pd.crosstab(index=df["rto_code"], columns=df["showroom_del"]).reindex(
        all_rto_code, fill_value=0
    )

    return result


def other_cases(df: pd.DataFrame, showrooms: List[str]) -> pd.DataFrame:
    valid_showrooms = [s for s in showrooms if s in df.columns]
    df["out_of_scope"] = df["Total Vehicles"] - (df[valid_showrooms].sum(axis=1))
    return df


def map_rto_to_city(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    df = df[df.index.notna()]
    df["RTO City"] = df.index.map(lambda x: mapping.get(x, "Unknown"))

    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)

    # Move "RTO City" after "RTOs"
    if "RTO City" in cols:
        cols.remove("RTO City")
        cols.insert(1, "RTO City")

    # Move "Showroom Total" to second last
    if "Showroom Total" in cols:
        cols.remove("Showroom Total")
        cols.insert(-1, "Showroom Total")

    return df[cols]


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

    # Total vehicles per RTO
    total_series = total_vehicles_per_rto(rto_recon).reindex(
        all_rto_codes, fill_value=0
    )
    crosstab_showroom_rto.insert(0, "Total Vehicles", total_series)

    showrooms = rto_recon["showroom_del"].dropna().unique().tolist()
    # Add Showroom Total
    crosstab_showroom_rto["Showroom Total"] = showroom_total(
        crosstab_showroom_rto, showrooms
    )

    # Add out_of_scope
    crosstab_showroom_rto["Out Of Scope"] = (
        crosstab_showroom_rto["Total Vehicles"]
        - crosstab_showroom_rto["Showroom Total"]
    )
    # Rename index
    crosstab_showroom_rto.index.name = "RTOs"

    crosstab_showroom_rto = map_rto_to_city(crosstab_showroom_rto, RTO_CITY_MAP)

    # Convert index to column
    crosstab_showroom_rto = crosstab_showroom_rto.reset_index()

    # Reorder columns
    crosstab_showroom_rto = reorder_columns(crosstab_showroom_rto)
    crosstab_showroom_rto.sort_index(inplace=True, ascending=False)

    return crosstab_showroom_rto
