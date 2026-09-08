import pandas as pd

from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

def train_xgboost(df: pd.DataFrame):

    df = df.copy()

    df["product_name"] = df["product"]

    df = pd.get_dummies(
        df,
        columns=["product"],
        dtype=int
    )

    df = df.dropna()

    split_index = int(len(df) * 0.8)

    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    feature_columns = [
        col
        for col in df.columns
        if col not in ["date", "amount", "product_name"]
    ]

    X_train = train_df[feature_columns]
    y_train = train_df["amount"]

    X_test = test_df[feature_columns]
    y_test = test_df["amount"]

    model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.08,
        obejctive="reg:squarederror",
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    predictions = predictions.clip(min=0)

    comparison = test_df[["date", "product_name", "amount"]].copy()

    comparison["predicted"] = predictions
    comparison["error"] = comparison["amount"] - comparison["predicted"]
    comparison["absolute_error"] = comparison["error"].abs()

    mae = mean_absolute_error(y_test, predictions)

    rmse = mean_squared_error(y_test, predictions) ** 0.5

    return{
        "model":model,
        "features": feature_columns,
        "mae": mae,
        "rmse": rmse,
        "comparison": comparison
           }
