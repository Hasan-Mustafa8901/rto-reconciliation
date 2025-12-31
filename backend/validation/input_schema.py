import pandas as pd
from typing import Dict, List, Optional


# Sheet Name Contracts
RTO_SHEET_NAME = "RTO Data"
DELIVERY_CURRENT_SHEET_NAME = "Delivery Data"
DELIVERY_PREVIOUS_SHEET_NAME = "Delivery Data (Previous)"   # optional

# Schema Definition
RTO_REQUIRED_COLUMNS = [
    "Office Name",
    "Dealer Name",
    "Vehicle Registration Number",
    "Owner Name",
    "Chassis Number",
]

DELIVERY_REQUIRED_COLUMNS = [
    "Delivery Date",
    "Customer Name",
    "Chassis Number",
    "Showroom",
]

# Validation Result Models

class ValidationError:
    def __init__(self, sheet: str, message: str) -> None:
        self.sheet = sheet
        self.message = message

    def __repr__(self) -> str:
        return f"[{self.sheet}] {self.message}"
    
class ValidationResult:
    def  __init__(self) -> None:
        self.is_valid: bool = True
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []

    def add_error(self, sheet: str, message: str):
        self.is_valid = False
        self.errors.append(ValidationError(sheet, message))

    def add_warning(self, message: str):
        self.warnings.append(message)

# Ingestion

def load_workbook(file_path: str) -> Dict[str, pd.DataFrame]:
    '''
    Loads all the sheet from the workbook.
    '''
    return pd.read_excel(file_path, sheet_name=None)


# Validatation Logic
def validate_rto_sheet(df: pd.DataFrame, result: ValidationResult):
    for col in RTO_REQUIRED_COLUMNS:
        if col not in df.columns:
            result.add_error("RTO Sheet", f"Missing Required Columns: {col}")

    if "Chassis Number" in df.columns:
        if df['Chassis Number'].isna().all():
            result.add_error("RTO Sheet", "All Chassis Number are Null.")
        
        if df['Chassis Number'].duplicated().any():
            result.add_warning("Duplicate Chassis Numbers found in RTO Sheet")

def validate_delivery_sheet(df: pd.DataFrame, sheet_name: str, result: ValidationResult):

    for col in DELIVERY_REQUIRED_COLUMNS:
        if col not in df.columns:
            result.add_error(sheet_name, f"Missing Required Columns: {col}")

    if "Chassis Number" in df.columns:
        if df['Chassis Number'].isna().all():
            result.add_error(sheet_name, "All Chassis Number are Null.")
        
        if df['Chassis Number'].duplicated().any():
            result.add_warning(f"Duplicate Chassis Numbers found in {sheet_name}")

# Pipeline Entry: Validation

def validate_workbook(file_path: str) -> ValidationResult:
    result = ValidationResult()
    
    # Load
    workbook = load_workbook(file_path)

    # Required sheets 
    if RTO_SHEET_NAME not in workbook:
        result.add_error("Workbook", "RTO Data not Found. Ensure sheet named 'RTO Data' exists.")

    if DELIVERY_CURRENT_SHEET_NAME not in workbook:
        result.add_error("Workbook", "Delivery Data not Found. Ensure sheet named 'Delivery Data' exists.")

    if not result.is_valid:
        return result
    
    validate_rto_sheet(workbook[RTO_SHEET_NAME], result)

    validate_delivery_sheet(
        workbook[DELIVERY_CURRENT_SHEET_NAME],
        DELIVERY_CURRENT_SHEET_NAME,
        result
        )
    # Optional previous month delivery sheet
    if DELIVERY_PREVIOUS_SHEET_NAME in workbook:
        validate_delivery_sheet(
            workbook[DELIVERY_PREVIOUS_SHEET_NAME],
            DELIVERY_PREVIOUS_SHEET_NAME,
            result
        )

    return result


