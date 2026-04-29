# Sheet Name Contracts
RTO_SHEET_NAME = "RTO Data" or "RTO Sheet"
DELIVERY_CURRENT_SHEET_NAME = "Delivery Data" or "Delivery Sheet"
DELIVERY_PREVIOUS_SHEET_NAME = "Delivery Data (Previous)"  # optional

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
BH_SERIES_PATTERN = r"^\d{2}BH\d{4}[A-Z]{1}$"
UP_SERIES_PATTERN = r"^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$"
NEW_SERIES_PATTERN = r"^NEW$"
TEMP_SERIES_PATTERN = r"^T\d{4}[A-Z]{2}\d{4}[A-Z]$"

CHASSIS_NUMBER_PATTERN = r"^[A-HJ-NPR-Z0-9]{17}$"
