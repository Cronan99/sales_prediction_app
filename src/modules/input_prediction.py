import pandas as pd

def prepare_prediction_row(
        historical_df: pd.DataFrame,
        feature_columns: list,
        product: str,
        price: float,
        prediction_date
):
    df = historical_df.copy()

    df["date"] = pd.to_datetime(df["date"])
    prediction_date = pd.to_datetime(prediction_date)

    product_history = df[
        (df["product"] == product) &
        (df["date"] < prediction_date)
    ].copy()

    product_history = product_history.sort_values("date")

    if len(product_history) < 28:
        raise ValueError(
            f"Not enough historical data for product '{product}' "
            f"before {prediction_date.date()}. "
            f"At least 28 days of history are required."
        )

    row = {
        "price": price,
        "day_of_week": prediction_date.dayofweek,
        "day_of_month": prediction_date.day,
        "month": prediction_date.month,
        "week_of_year": prediction_date.isocalendar().week,

        "lag_1": product_history["amount"].iloc[-1],
        "lag_7": product_history["amount"].iloc[-7],
        "lag_14": product_history["amount"].iloc[-14],

        "rolling_mean_7": product_history["amount"].tail(7).mean(),
        "rolling_mean_14": product_history["amount"].tail(14).mean(),
    }

    prediction_df = pd.DataFrame(
        0.0,
        index=[0],
        columns=feature_columns
    )

    for column, value in row.items():
        if column in prediction_df.columns:
            prediction_df.loc[0, column] = value

    product_column = f"product_{product}"

    if product_column not in feature_columns:
        raise ValueError(
            f"Product '{product}' was not present when the model was trained."

        )

    prediction_df.loc[0, product_column] = 1

    return prediction_df