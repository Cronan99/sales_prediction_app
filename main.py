from src.data_loader import load_sales_data
from src.model import create_baseline_predictions, evaluate_baseline


df = load_sales_data("data/fishmonger_sales.csv")

df = create_baseline_predictions(df)

metrics = evaluate_baseline(df)

print(
    df[
        [
            "date",
            "product",
            "amount",
            "baseline_prediction",
        ]
    ].head(20)
)
print(f"Baseline MAE: {metrics['mae']:.2f}")
print(f"Baseline RMSE: {metrics['rmse']:.2f}")