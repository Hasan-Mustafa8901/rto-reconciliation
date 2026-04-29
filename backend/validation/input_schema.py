import pandas as pd
from typing import Dict, List
from backend.constant import (
    RTO_REQUIRED_COLUMNS,
    RTO_SHEET_NAME,
    DELIVERY_CURRENT_SHEET_NAME,
    DELIVERY_PREVIOUS_SHEET_NAME,
    DELIVERY_REQUIRED_COLUMNS,
    UP_SERIES_PATTERN,
    BH_SERIES_PATTERN,
    # TEMP_SERIES_PATTERN,
    # NEW_SERIES_PATTERN,
    CHASSIS_NUMBER_PATTERN,
)


def build_violation_table(
    df: pd.DataFrame,
    mask: pd.Series,
    columns: list,
    max_rows: int | None = None,
) -> pd.DataFrame:
    """
    Returns a tabular DataFrame showing rows that caused validation failure.
    Includes Excel-friendly row numbers.
    """

    # Filter only violating rows
    vdf = df.loc[mask, columns].copy()

    # Add row numbers (Excel-style)
    vdf = vdf.reset_index().rename(columns={"index": "Row"})
    vdf["Row"] = vdf["Row"] + 2  # adjust for header row

    # Limit rows if needed
    if max_rows:
        vdf = vdf.head(max_rows)

    return vdf


# Validation Result Models
def build_violation_message(df, mask, column, base_message, max_examples=None):
    bad_values = df.loc[mask, column]

    # Get sample values
    sample_values = bad_values.dropna().astype(str).unique()[:max_examples]

    # Get row numbers (Excel-friendly → +2 for header)
    if max_examples:
        row_numbers = (bad_values.index + 2).tolist()[:max_examples]
    row_numbers = (bad_values.index + 2).tolist()

    return f"{base_message}. Examples: {list(sample_values)} at rows {row_numbers}"


class ValidationError:
    def __init__(self, sheet: str, message: str) -> None:
        self.sheet = sheet
        self.message = message

    def __repr__(self) -> str:
        return f"[{self.sheet}] {self.message}"


class ValidationWarning:
    def __init__(self, sheet: str, message: str) -> None:
        self.sheet = sheet
        self.message = message

    def __repr__(self) -> str:
        return f"[{self.sheet}] {self.message}"


class ValidationResult:
    def __init__(self) -> None:
        self.is_valid: bool = True
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []

    def add_error(self, sheet: str, message: str):
        self.is_valid = False
        self.errors.append(ValidationError(sheet, message))

    def add_warning(self, sheet: str, message: str):
        self.warnings.append(ValidationWarning(sheet, message))


# Ingestion


def load_workbook(file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Loads all the sheet from the workbook.
    """
    return pd.read_excel(file_path, sheet_name=None)


# Validation Helpers
def validate_null_column(df, column, sheet, result):
    if column in df.columns:
        mask = df[column].isna()
        if mask.all():
            result.add_warning(sheet, f"All {column} are Null.")
        return mask
    return pd.Series(False, index=df.index)


def validate_duplicates(df, column, sheet, result):
    if column in df.columns:
        series = df[column]
        mask = series.notna() & series.duplicated(keep=False)
        if mask.any():
            result.add_warning(sheet, f"Duplicate {column} found in {sheet}")
        return mask
    return pd.Series(False, index=df.index)


# def validate_pattern(df, column, pattern, sheet, result, message):
#     if column in df.columns:
#         series = df[column]
#         mask = series.notna() & ~series.astype(str).str.match(pattern, na=False)
#         if mask.any():
#             result.add_warning(sheet, message)
#         return mask
#     return pd.Series(False, index=df.index)


def validate_pattern(
    df,
    column,
    sheet,
    result,
    message,
    patterns: list,
):
    if column in df.columns:
        series = df[column]
        s = series.astype(str).str.strip()

        # Combine all valid patterns
        valid_mask = False
        for p in patterns:
            valid_mask |= s.str.match(p)

        mask = series.notna() & ~valid_mask

        if mask.any():
            result.add_warning(sheet, message)

        return mask

    return pd.Series(False, index=df.index)


def validate_length(df, column, max_len, sheet, result):
    if column in df.columns:
        mask = df[column].astype(str).str.len().gt(max_len)
        if mask.any():
            result.add_warning(sheet, f"{column} length exceeds {max_len} in {sheet}")
        return mask
    return pd.Series(False, index=df.index)


def validate_required_columns(df, required_cols, sheet, result):
    for col in required_cols:
        if col not in df.columns:
            result.add_error(sheet, f"Missing Required Column: {col}")


def validate_rto_sheet(df: pd.DataFrame, result: ValidationResult):
    sheet = "RTO Sheet"
    violations = {}

    validate_required_columns(df, RTO_REQUIRED_COLUMNS, sheet, result)

    # --- Chassis Number
    mask = validate_null_column(df, "Chassis Number", sheet, result)
    if mask.any():
        violations["null_chassis"] = df[mask]

    mask = validate_duplicates(df, "Chassis Number", sheet, result)
    if mask.any():
        violations["duplicate_chassis"] = df[mask]

    mask = validate_pattern(
        df,
        "Chassis Number",
        sheet,
        result,
        "Invalid Chassis Number format in RTO Sheet",
        patterns=[CHASSIS_NUMBER_PATTERN, r"^\d{6}$"],
    )
    if mask.any():
        violations["invalid_chassis_format"] = build_violation_table(
            df, mask, ["Chassis Number", "Vehicle Registration Number"]
        )

    # --- Vehicle Registration Number
    mask = validate_null_column(df, "Vehicle Registration Number", sheet, result)
    if mask.any():
        violations["null_vrn"] = df[mask]

    mask = validate_duplicates(df, "Vehicle Registration Number", sheet, result)
    if mask.any():
        violations["duplicate_vrn"] = build_violation_table(
            df, mask, ["Vehicle Registration Number"]
        )

    mask = validate_length(df, "Vehicle Registration Number", 10, sheet, result)
    if mask.any():
        violations["vrn_length_exceeded"] = df[mask]

    mask = validate_pattern(
        df,
        "Vehicle Registration Number",
        sheet,
        result,
        "Invalid Vehicle Registration Number format in RTO Sheet",
        patterns=[BH_SERIES_PATTERN, UP_SERIES_PATTERN],
    )
    if mask.any():
        violations["invalid_vrn_format"] = build_violation_table(
            df, mask, ["Vehicle Registration Number", "Owner Name"]
        )

    return violations


def validate_delivery_sheet(
    df: pd.DataFrame, sheet_name: str, result: ValidationResult
):
    violations = {}

    # --- Required Columns
    validate_required_columns(df, DELIVERY_REQUIRED_COLUMNS, sheet_name, result)

    # --- Chassis Number
    mask = validate_null_column(df, "Chassis Number", sheet_name, result)
    if mask.any():
        violations["null_chassis"] = df[mask]

    mask = validate_duplicates(df, "Chassis Number", sheet_name, result)
    if mask.any():
        violations["duplicate_chassis"] = df[mask]

    mask = validate_pattern(
        df,
        "Chassis Number",
        sheet_name,
        result,
        f"Invalid Chassis Number format in {sheet_name}",
        patterns=[CHASSIS_NUMBER_PATTERN, r"^\d{6}$"],
    )
    if mask.any():
        violations["invalid_chassis_format"] = build_violation_table(
            df, mask, ["Customer Name", "Chassis Number"]
        )

    # --- (Optional but practical) Delivery Date checks
    if "Delivery Date" in df.columns:
        mask = df["Delivery Date"].isna()
        if mask.any():
            result.add_warning(sheet_name, f"Missing Delivery Date in {sheet_name}")
            violations["missing_delivery_date"] = df[mask]

    return violations


# Pipeline Entry: Validation


def validate_workbook(file_path: str) -> tuple[ValidationResult, dict]:
    result = ValidationResult()
    all_violations = {}

    # Load
    workbook = load_workbook(file_path)

    # Required sheets
    if RTO_SHEET_NAME not in workbook:
        result.add_error(
            "Workbook", "RTO Data not Found. Ensure sheet named 'RTO Data' exists."
        )

    if DELIVERY_CURRENT_SHEET_NAME not in workbook:
        result.add_error(
            "Workbook",
            "Delivery Data not Found. Ensure sheet named 'Delivery Data' exists.",
        )

    if not result.is_valid:
        return result, all_violations

    rto_violations = validate_rto_sheet(workbook[RTO_SHEET_NAME], result)
    all_violations["rto"] = rto_violations

    delivery_violations = validate_delivery_sheet(
        workbook[DELIVERY_CURRENT_SHEET_NAME], DELIVERY_CURRENT_SHEET_NAME, result
    )
    all_violations["delivery"] = delivery_violations

    # Optional previous month delivery sheet
    if DELIVERY_PREVIOUS_SHEET_NAME in workbook:
        previous_violations = validate_delivery_sheet(
            workbook[DELIVERY_PREVIOUS_SHEET_NAME], DELIVERY_PREVIOUS_SHEET_NAME, result
        )
        all_violations["delivery_previous"] = previous_violations

    return result, all_violations
