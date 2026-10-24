from pathlib import Path

import pandas as pd
import joblib

from src.modules.data_loader import load_sales_data
from src.features import create_features
from src.model import train_xgboost
from src.modules.input_prediction import prepare_prediction_row


# Configuration
DATASET = "data/butcher_shop_sales_2025_5500.csv"
MAPPING = "retail_sales"

OUTPUT_DIR = Path("model")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    # 1. Load dataset
    df = load_sales_data(
        DATASET,
        mapping=MAPPING
    )

    # Save aggregated daily sales
    df.to_csv("data/processed_daily_sales.csv", index=False)

    print("Processed daily sales saved!")

    print(f"Loaded {len(df)} sales records.")
    print(f"Available products: {df['product'].unique()}")

    # 2. Create features
    df = create_features(df)

    # 3. Train model
    results = train_xgboost(df)

    print(f"MAE: {results['mae']:.2f}")
    print(f"RMSE: {results['rmse']:.2f}")

    results["comparison"].to_csv(
        "data/predictions.csv",
        index=False
    )

    # 4. Select product automatically
    available_products = sorted(df["product"].unique())

    PRODUCT = available_products[0]

    # 5. Select prediction date automatically
    DATE = (
        df["date"].max() + pd.Timedelta(days=1)
    ).strftime("%Y-%m-%d")

    # 6. Estimate price from historical data
    PRICE = df.loc[
        df["product"] == PRODUCT, "price"
    ].median()

    print(f"\nPredicting sales for:")
    print(f"Product: {PRODUCT}")
    print(f"Date: {DATE}")
    print(f"Price: {PRICE:.2f}")

    # 7. Prepare prediction
    prediction_row = prepare_prediction_row(
        historical_df=df,
        feature_columns=results["features"],
        product=PRODUCT,
        price=PRICE,
        prediction_date=DATE
    )

    # 8. Predict
    model = results["model"]

    prediction = model.predict(prediction_row)[0]
    prediction = max(0, prediction)

    print(
        f"Predicted sales for {PRODUCT} "
        f"on {DATE} at price {PRICE:.2f}: "
        f"{prediction:.2f}"
    )

    # 9. Feature importance
    importance = pd.DataFrame({
        "feature": results["features"],
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    print("\nFeature importance:")
    print(importance)

    # 10. Save model
    joblib.dump(
        model,
        OUTPUT_DIR / "sales_model.pkl"
    )

    joblib.dump(
        results["features"],
        OUTPUT_DIR / "feature_columns.pkl"
    )


if __name__ == "__main__":
    main()