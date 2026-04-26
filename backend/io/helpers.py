import pandas as pd


def add_serial_number(df: pd.DataFrame, col_name: str = "S.No.") -> pd.DataFrame:
    df = df.reset_index(drop=True).copy()

    # Remove existing column if already present
    if col_name in df.columns:
        df = df.drop(columns=[col_name])

    df.insert(0, col_name, range(1, len(df) + 1))
    return df
