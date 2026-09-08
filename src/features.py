import pandas as pd

def create_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df = df.sort_values(["product", "date"])

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    df["lag_1"] = (
        df.groupby("product")["amount"].shift(1)
    )

    df["lag_7"] = (
        df.groupby("product")["amount"].shift(7)
    )

    df["lag_14"] = (
        df.groupby("product")["amount"].shift(14)
    )

    df["rolling_mean_7"] = (
        df.groupby("product")["amount"].transform(
            lambda x: x.shift(1).rolling(7).mean()
        )
    )

    df["rolling_mean_28"] = (
        df.groupby("product")["amount"].transform(
            lambda x: x.shift(1).rolling(28).mean()
        )
    )

    return df