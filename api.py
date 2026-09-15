from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import joblib
import pandas as pd

from src.modules.input_prediction import prepare_prediction_row

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model/sales_model.pk1")
feature_columns = joblib.load("model/feature_columns.pk1")

historical_df = pd.read_csv("data/fishmonger_sales.csv")

historical_df["date"] = pd.to_datetime(historical_df["date"])


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