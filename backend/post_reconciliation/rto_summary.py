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


def add_total_row(df: pd.DataFrame, label: str = "Total") -> pd.DataFrame:
    """
    Adds a total row at the end of RTO summary dataframe.
    Sums numeric columns and labels the row.
    """
    df = df.copy()

    # Identify numeric columns
    numeric_cols = df.select_dtypes(include="number").columns

    # Create total row
    total_row = {
        col: df[col].sum() if col in numeric_cols else "" for col in df.columns
    }

    # Set label (usually first column is 'RTOs')
    first_col = df.columns[0]
    total_row[first_col] = label

    # Append row
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    return df


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


def prioritize_and_sort(
    df: pd.DataFrame,
    column: str,
    priority: list,
    sort_by: str | None = None,
    ascending: bool = True,
    keep_total_last: bool = True,
) -> pd.DataFrame:
    df = df.copy()

    # --- Separate total row if needed
    if keep_total_last and column in df.columns:
        total_df = df[df[column] == "Total"]
        df = df[df[column] != "Total"]
    else:
        total_df = pd.DataFrame()

    # --- Priority rows
    priority_df = df[df[column].isin(priority)].copy()
    priority_df["_order"] = priority_df[column].apply(lambda x: priority.index(x))
    priority_df = priority_df.sort_values("_order").drop(columns="_order")

    # --- Remaining rows
    remaining_df = df[~df[column].isin(priority)]

    if sort_by:
        remaining_df = remaining_df.sort_values(by=sort_by, ascending=ascending)
    else:
        remaining_df = remaining_df.sort_values(by=column, ascending=ascending)

    # --- Combine all
    final_df = pd.concat([priority_df, remaining_df, total_df], ignore_index=True)

    return final_df


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
    crosstab_showroom_rto = prioritize_and_sort(
        crosstab_showroom_rto,
        column="RTOs",
        priority=["UP32"],
        sort_by="Total Vehicles",
        ascending=False,
    )
    # Add Total Row
    crosstab_showroom_rto = add_total_row(crosstab_showroom_rto)

    return crosstab_showroom_rto
