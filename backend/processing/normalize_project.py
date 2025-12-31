# normalize_project.py
import pandas as pd
from typing import Dict, Optional


# =========================
# Column Mapping
# =========================

RTO_COLUMN_MAP = {
    "Office Name": "office_name_rto",
    "Dealer Name": "dealer_name_rto",
    "Vehicle Registration Number": "registration_no_rto",
    "Owner Name": "owner_name_rto",
    "Chassis Number": "chassis_no_rto",
}

DELIVERY_COLUMN_MAP = {
    "Delivery Date": "delivery_date_del",
    "Customer Name": "customer_name_del",
    "Chassis Number": "chassis_no_del",
    "Showroom": "showroom_del",
}
PREVIOUS_DELIVERY_COLUMN_MAP = {
    "Delivery Date": "delivery_date_prev",
    "Customer Name": "customer_name_prev",
    "Chassis Number": "chassis_no_prev",
    "Showroom": "showroom_prev",
}


# =========================
# Utility Normalizers
# =========================

def normalize_string(series: pd.Series) -> pd.Series:
    """Trim whitespace and standardize string casing."""
    return (
        series.astype(str)
        .str.strip()
        .replace({"nan": None})
    )


def normalize_chassis(series: pd.Series) -> pd.Series:
    """Canonical normalization for Chassis Number."""
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .replace({"nan": None})
    )

def resolve_chassis_and_vin(value: str):
    '''
    Resolves whether the value is a full chassis number or a VIN.
    :param value: Description
    :type value: str
    '''
    if value is None:
        return None, None, "INVALID"
    
    value = str(value).strip().upper()

    if len(value) > 6:
        return value, value[-6:], "CHASSIS"
    
    if len(value) < 6:
        return None, value.zfill(6), "VIN"
    if len(value) == 6:
        return None, value, "VIN"
    
    return None, None, "INVALID"


# =========================
# RTO Normalization
# =========================

def normalize_rto_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and project RTO Data to canonical schema.
    """
    # 1. Select required columns only
    df = df[list(RTO_COLUMN_MAP.keys())].copy()

    # 2. Rename columns
    df.rename(columns=RTO_COLUMN_MAP, inplace=True)

    # 3. Normalize fields
    df["office_name_rto"] = normalize_string(df["office_name_rto"])
    df["dealer_name_rto"] = normalize_string(df["dealer_name_rto"])
    df["registration_no_rto"] = normalize_string(df["registration_no_rto"])
    df["owner_name_rto"] = normalize_string(df["owner_name_rto"])
    df["rto_code"] = df["registration_no_rto"].str[0:4]
    df["chassis_no_rto"] = normalize_chassis(df["chassis_no_rto"])
    df["vin_rto"] = df["chassis_no_rto"].str[-6:]
    df["id_source"] = "CHASSIS"

    return df


# =========================
# Delivery Normalization
# =========================
## Refactor break into small mehtods
def normalize_delivery_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and project Delivery Data.
    Handles:
    - Chassis Number column
    - VIN Number column
    """
    # ---- detect identifier column ----
    if "Chassis Number" in df.columns:
        identifier_col = "Chassis Number"
    elif "VIN Number" in df.columns:
        identifier_col = "VIN Number"
    else:
        raise ValueError(
            "Delivery Data must contain either 'Chassis Number' or 'VIN Number'"
        )

    # ---- select required columns dynamically ----
    base_cols = ["Delivery Date", "Customer Name", "Showroom", identifier_col]
    df = df[base_cols].copy()

    # ---- rename non-identifier columns ----
    df.rename(
        columns={
            "Delivery Date": "delivery_date_del",
            "Customer Name": "customer_name_del",
            "Showroom": "showroom_del",
        },
        inplace=True,
    )

    # ---- normalize basic fields ----
    df["delivery_date_del"] = normalize_string(df["delivery_date_del"])
    df["customer_name_del"] = normalize_string(df["customer_name_del"])
    df["showroom_del"] = normalize_string(df["showroom_del"])

    # ---- normalize identifier ----
    raw_id = (
        df[identifier_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["raw_identifier"] = raw_id

    def resolve_identifier(val):
        if not val or val == "NAN":
            return None, None, "INVALID"

        if len(val) > 6:
            return val, val[-6:], "CHASSIS"
        
        if len(val) < 6:
            return None, val.zfill(6)[0:6], "VIN"

        if len(val) == 6:
            return None, val, "VIN"

        return None, None, "INVALID"

    resolved = raw_id.apply(resolve_identifier)

    df["chassis_no_del"] = resolved.apply(lambda x: x[0])
    df["vin_del"] = resolved.apply(lambda x: x[1])
    df["id_source"] = resolved.apply(lambda x: x[2])

    # Drop the raw identifier column
    df.drop(columns=[identifier_col], inplace=True)

    return df

def normalize_previous_delivery_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and project Previous Delivery Data.

    Row-level identifier resolution:
    - Prefer Chassis Number if present
    - Else fallback to VIN Number
    """

    # ---- required base columns ----
    required_cols = {"Delivery Date", "Customer Name", "Showroom"}
    identifier_cols = {"Chassis Number", "VIN Number"}

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if not identifier_cols.intersection(df.columns):
        raise ValueError(
            "Delivery Data must contain at least one of: 'Chassis Number', 'VIN Number'"
        )

    # ---- select available columns ----
    cols_to_select = list(required_cols | identifier_cols)
    df = df[cols_to_select].copy()

    # ---- rename base columns ----
    df.rename(
        columns={
            "Delivery Date": "delivery_date_prev",
            "Customer Name": "customer_name_prev",
            "Showroom": "showroom_prev",
        },
        inplace=True,
    )

    # ---- normalize base fields ----
    df["delivery_date_prev"] = normalize_string(df["delivery_date_prev"])
    df["customer_name_prev"] = normalize_string(df["customer_name_prev"])
    df["showroom_prev"] = normalize_string(df["showroom_prev"])

    # ---- normalize identifiers (row-level fallback) ----
    chassis_series = (
        df["Chassis Number"].astype(str).str.strip().str.upper()
        if "Chassis Number" in df.columns
        else None
    )

    vin_series = (
        df["VIN Number"].astype(str).str.strip().str.upper()
        if "VIN Number" in df.columns
        else None
    )

    def resolve_identifier(row):
        chassis = (
            chassis_series.loc[row.name]
            if chassis_series is not None
            else None
        )
        vin = (
            vin_series.loc[row.name]
            if vin_series is not None
            else None
        )

        # clean null-like values
        if chassis in ("", "NAN", "NONE"):
            chassis = None
        if vin in ("", "NAN", "NONE"):
            vin = None

        # Prefer chassis if present
        if chassis:
            return chassis, chassis[-6:], "CHASSIS"

        # Fallback to VIN
        if vin:
            vin = vin.zfill(6)
            return None, vin, "VIN"

        # Invalid
        return None, None, "INVALID"

    resolved = df.apply(resolve_identifier, axis=1)

    df["chassis_no_prev"] = resolved.apply(lambda x: x[0])
    df["vin_prev"] = resolved.apply(lambda x: x[1])
    df["id_source"] = resolved.apply(lambda x: x[2])

    # ---- drop raw identifier columns ----
    drop_cols = [c for c in ["Chassis Number", "VIN Number"] if c in df.columns]
    df.drop(columns=drop_cols, inplace=True)

    return df

# =========================
# Pipeline Entry: Projection
# =========================

def normalize_and_project(
    workbook: Dict[str, pd.DataFrame],
    *,
    rto_sheet: str,
    delivery_current_sheet: str,
    delivery_previous_sheet: Optional[str] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Applies normalization and projection to validated workbook.
    """

    normalized = {
        "rto": normalize_rto_data(workbook[rto_sheet]),
        "delivery_current": normalize_delivery_data(workbook[delivery_current_sheet]),
    }

    if delivery_previous_sheet and delivery_previous_sheet in workbook:
        normalized["delivery_previous"] = normalize_previous_delivery_data(
            workbook[delivery_previous_sheet]
        )

    return normalized