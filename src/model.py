import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def create_baseline_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a naive sales forecast.

    Baseline:
    Predict that each product will sell the same amount
    as it did on its previous recorded sale date.
    """
    df = df.copy()
    df = df.sort_values(["product", "date"])

    df["baseline_prediction"] = (
        df.groupby("product")["amount"]
        .shift(1)
    )

    return df


def evaluate_baseline(df: pd.DataFrame) -> dict:
    """
    Evaluate baseline predictions using MAE and RMSE.
    """

    evaluation_df = df.dropna(subset=["baseline_prediction"])

    y_true = evaluation_df["amount"]
    y_pred = evaluation_df["baseline_prediction"]

    mae = mean_absolute_error(y_true, y_pred)

    rmse = mean_squared_error(
        y_true,
        y_pred
    ) ** 0.5

    return {
        "mae": mae,
        "rmse": rmse,
    }