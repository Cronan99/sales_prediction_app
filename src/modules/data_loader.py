
from pathlib import Path

import pandas as pd

from ..columns_mappings import COLUMN_MAPPINGS


REQUIRED_COLUMNS = {"date", "product", "amount", "price"}


def aggregate_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transactions into daily sales per product.

    Amount: Total quantity sold per day.
    Price: Quantity-weighted average selling price.
    """

    df = df.copy()

    # Calculate revenue per transaction
    df["revenue"] = df["amount"] * df["price"]

    # Aggregate by date and product
    daily = (
        df.groupby(["date", "product"], as_index=False)
        .agg(
            amount=("amount", "sum"),
            revenue=("revenue", "sum")
        )
    )

    # Calculate weighted average price
    daily["price"] = (
        daily["revenue"] / daily["amount"].replace(0, float("nan"))
    )

    return (
        daily[["date", "product", "amount", "price"]]
        .sort_values(["product", "date"])
        .reset_index(drop=True)
    )


def load_sales_data(
    file_path: str | Path,
    mapping: str = "retail_sales",
    aggregate_daily: bool = True
) -> pd.DataFrame:
    """
    Load sales data from a CSV file and standardize columns.

    Args:
        file_path: Path to the CSV file.
        mapping: Name of the column mapping configuration.
        aggregate_daily: Aggregate transactions into daily totals.

    Returns:
        pd.DataFrame: Validated and standardized sales data.
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"The file {file_path} does not exist."
        )

    if mapping not in COLUMN_MAPPINGS:
        raise ValueError(
            f"Unknown mapping '{mapping}'. "
            f"Available mappings: {list(COLUMN_MAPPINGS)}"
        )

    df = pd.read_csv(file_path)

    # Apply column mapping
    df = df.rename(columns=COLUMN_MAPPINGS[mapping])

    # Validate required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Keep only required columns
    df = df[["date", "product", "amount", "price"]].copy()

    # Convert data types
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")
    df["price"] = pd.to_numeric(df["price"], errors="raise")

    # Validate data
    if df.isna().any().any():
        raise ValueError("Sales data contains missing values.")

    if (df["amount"] < 0).any():
        raise ValueError("Sales quantities cannot be negative.")

    if (df["price"] < 0).any():
        raise ValueError("Prices cannot be negative.")

    # Aggregate transactions if requested
    if aggregate_daily:
        df = aggregate_daily_sales(df)

    return df
