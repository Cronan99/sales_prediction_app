from src.data_loader import load_sales_data
from src.features import create_features
from src.model import train_xgboost

df = load_sales_data("data/fishmonger_sales .csv")

df = create_features(df)

results = train_xgboost(df)

print(f"MAE: {results['mae']:.2f}")
print(f"RMSE: {results['rmse']:.2f}")

results["comparison"].to_csv("data/predictions.csv", index=False)