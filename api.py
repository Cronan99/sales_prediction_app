from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import joblib

from src.modules.input_prediction import prepare_prediction_row
from src.modules.data_loader import load_sales_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model/sales_model.pkl")
feature_columns = joblib.load("model/feature_columns.pkl")

DATASET = "data/butcher_shop_sales_2025_5500.csv"
MAPPING = "retail_sales"

historical_df = load_sales_data(DATASET, mapping=MAPPING)


class PredictionRequest(BaseModel):
    product: str
    price: float
    date: str

@app.get("/")
def root():
    return {"status": "Prediction API is running!"}


@app.post("/predict")
def predict_sales(request: PredictionRequest):
    prediction_row = prepare_prediction_row(
        historical_df=historical_df,
        feature_columns=feature_columns,
        product=request.product,
        price=request.price,
        prediction_date=request.date
    )

    prediction = model.predict(prediction_row)[0]

    prediction = float(prediction)
    prediction = max(0.0, prediction)
    prediction = round(prediction, 2)

    return {
        "product": request.product,
        "price": request.price,
        "date": request.date,
        "predicted_sales": prediction
    }

@app.get("/products")
def get_products():
    df = load_sales_data(DATASET, mapping=MAPPING)

    products = []

    for product, group in df.groupby("product"):
        products.append({
            "name": product,
            "min": round(float(group["price"].min()), 2),
            "max": round(float(group["price"].max()), 2),
            "price": round(float(group["price"].median()), 2)
        })

    return products