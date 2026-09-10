from src.modules.data_loader import load_sales_data
from src.features import create_features
from src.model import train_xgboost
from src.modules.input_prediction import prepare_prediction_row
import pandas as pd
import joblib



df = load_sales_data("data/fishmonger_sales.csv")

df = create_features(df)

results = train_xgboost(df)

print(f"MAE: {results['mae']:.2f}")
print(f"RMSE: {results['rmse']:.2f}")

results["comparison"].to_csv("data/predictions.csv", index=False)

PRICE = 10
DATE = "2026-09-11"
PRODUCT = "Salmon"

prediction_row = prepare_prediction_row(
    historical_df=df,
    feature_columns=results["features"],
    product=PRODUCT,
    price=PRICE,
    prediction_date=DATE
)

model = results["model"]

prediction = model.predict(prediction_row)[0]

prediction = max(0, prediction)

print(f"Predicted sales for {PRODUCT} on {DATE} at price {PRICE}: {prediction:.2f}")

model = results["model"]
features = results["features"]

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print(importance)

joblib.dump(results["model"], "model/sales_model.pk1")
joblib.dump(results["features"], "model/feature_columns.pk1")