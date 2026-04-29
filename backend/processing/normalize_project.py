# normalize_project.py
import pandas as pd
from typing import Dict, Optional
from backend.constant import RTO_REQUIRED_COLUMNS


# =========================
# Column Mapping
# =========================

RTO_COLUMN_MAP = {
    "Office Name": "office_name_rto",
    "Dealer Name": "dealer_name_rto",
    "Vehicle Registration Number": "registration_no_rto",
    "Owner Name": "owner_name_rto",
    "Registration Date": "registration_date_rto",
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
    return series.astype(str).str.strip().replace({"nan": None})


def normalize_chassis(series: pd.Series) -> pd.Series:
    """Canonical normalization for Chassis Number."""
    return series.astype(str).str.strip().str.upper().replace({"nan": None})


def clean_identifier(value) -> Optional[str]:
    """
    Cleans raw identifier values coming from Excel.
    Handles:
    - float values with .0
    - scientific notation
    - leading zeros
    - NaN / None
    """
    if pd.isna(value):
        return None

    # Convert to string safely
    val = str(value).strip()

    if val.lower() in ("nan", "none", ""):
        return None

    # Remove trailing .0 (Excel float issue)
    if val.endswith(".0"):
        val = val[:-2]

    # Remove scientific notation artifacts
    if "e+" in val.lower():
        try:
            val = f"{int(float(val))}"
        except ValueError:
            return None

    return val.upper()


def resolve_chassis_and_vin(raw_value: Optional[str]):
    """
    Canonical identifier resolver.

    Returns:
    (chassis_no, vin, id_source)
    """

    if not raw_value:
        return None, None, "INVALID"

    val = raw_value

    # Chassis: longer than 6 chars
    if len(val) > 6:
        return val, val[-6:], "CHASSIS"

    # VIN: exactly or less than 6 digits
    if len(val) <= 6 and val.isdigit():
        return None, val.zfill(6), "VIN"

    return None, None, "INVALID"


# =========================
# RTO Normalization
# =========================


def normalize_rto_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and project RTO Data to canonical schema.
    """
    # 1. Select required columns only
    missing_required = [col for col in RTO_REQUIRED_COLUMNS if col not in df.columns]
    if missing_required:
        ValueError(f"Missing Required Columns:{missing_required}")

    cols = RTO_REQUIRED_COLUMNS.copy()
    if "Registraion Date" in df.columns:
        cols.append("Registration Date")

    df = df[cols].copy()

    # 2. Rename columns
    df.rename(columns=RTO_COLUMN_MAP, inplace=True)

    # 3. Normalize fields
    df["office_name_rto"] = normalize_string(df["office_name_rto"])
    df["dealer_name_rto"] = normalize_string(df["dealer_name_rto"])
    df["registration_no_rto"] = normalize_string(df["registration_no_rto"])
    df["owner_name_rto"] = normalize_string(df["owner_name_rto"])
    df["rto_code"] = df["registration_no_rto"].str[0:4]
    df["chassis_no_rto"] = df["chassis_no_rto"].apply(clean_identifier)
    df["vin_rto"] = df["chassis_no_rto"].str[-6:]
    # df["id_source"] = "CHASSIS"
    if "registraion_date_rto" in df.columns:
        df["registration_date_rto"] = normalize_string(df["registration_date_rto"])
    else:
        df["registration_date_rto"] = None

    return df


def normalize_delivery_data(
    df: pd.DataFrame,
    *,
    suffix: str,
) -> pd.DataFrame:
    """
    Normalize delivery-like data (current or previous).

    suffix:
        "del"  -> current delivery
        "prev" -> previous delivery
    """

    required_cols = {"Delivery Date", "Customer Name", "Showroom"}
    id_cols = {"Chassis Number", "VIN Number"}

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if not id_cols.intersection(df.columns):
        raise ValueError(
            "Delivery data must contain at least one of: "
            "'Chassis Number' or 'VIN Number'"
        )

    df = df.copy()

    # -----------------------------
    # Normalize base fields
    # -----------------------------
    df[f"delivery_date_{suffix}"] = normalize_string(df["Delivery Date"])
    df[f"customer_name_{suffix}"] = normalize_string(df["Customer Name"])
    df[f"showroom_{suffix}"] = normalize_string(df["Showroom"])

    # -----------------------------
    # Resolve identifiers (row-wise)
    # -----------------------------
    def resolve_row(row):
        chassis = clean_identifier(row.get("Chassis Number"))
        vin = clean_identifier(row.get("VIN Number"))

        raw = chassis or vin
        return resolve_chassis_and_vin(raw)

    resolved = df.apply(resolve_row, axis=1)

    df[f"chassis_no_{suffix}"] = resolved.apply(lambda x: x[0])
    df[f"vin_{suffix}"] = resolved.apply(lambda x: x[1])
    df[f"id_source_{suffix}"] = resolved.apply(lambda x: x[2])

    # -----------------------------
    # Drop raw columns
    # -----------------------------
    drop_cols = [
        "Delivery Date",
        "Customer Name",
        "Showroom",
        "Chassis Number",
        "VIN Number",
    ]
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

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
        "delivery_current": normalize_delivery_data(
            workbook[delivery_current_sheet], suffix="del"
        ),
    }

    if delivery_previous_sheet and delivery_previous_sheet in workbook:
        normalized["delivery_previous"] = normalize_delivery_data(
            workbook[delivery_previous_sheet],
            suffix="prev",
        )

    return normalized
