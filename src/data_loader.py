from pathlib import Path
import re

import pandas as pd

REQUIRED_COLUMNS = ["date", "product_name", "amount_sold", "price_per_unit"]

def load_sales_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load sales data from a CSV file and validate its structure.

    Expected columns:
    - Date
    - Product Name
    - Amount Sold
    - Price per Unit

    Returns:
        pd.DataFrame: A loaded and validated DataFrame containing the sales data.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    df = pd.read_csv(file_path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}."
        )

    df["date"] = pd.to_datetime(df[df["date"]])

    df["amount_sold"] = pd.to_numeric(df["amount_sold"], errors="raise")
    df["price_per_unit"] = pd.to_numeric(df["price_per_unit"], errors="raise")

    return df