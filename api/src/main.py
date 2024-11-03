from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from typing import Dict

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="API for detecting fraudulent credit card transactions",
    version="1.0.0",
)


# Define transaction model
class Transaction(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float

    class Config:
        schema_extra = {
            "example": {
                "Time": 9.0,
                "V1": -0.33826175242575,
                "V2": 1.11959337641566,
                "V3": 1.04436655157316,
                "V4": -0.222187276738296,
                "V5": 0.49936080649727,
                "V6": -0.24676110061991,
                "V7": 0.651583206489972,
                "V8": 0.0695385865186387,
                "V9": -0.736727316364109,
                "V10": -0.366845639206541,
                "V11": 1.01761446783262,
                "V12": 0.836389570307029,
                "V13": 1.00684351373408,
                "V14": -0.443522816876142,
                "V15": 0.150219101422635,
                "V16": 0.739452777052119,
                "V17": -0.540979921943059,
                "V18": 0.47667726004282,
                "V19": 0.451772964394125,
                "V20": 0.203711454727929,
                "V21": -0.246913936910008,
                "V22": -0.633752642406113,
                "V23": -0.12079408408185,
                "V24": -0.385049925313426,
                "V25": -0.0697330460416923,
                "V26": 0.0941988339514961,
                "V27": 0.246219304619926,
                "V28": 0.0830756493473326,
                "Amount": 3.68,
            }
        }


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    timestamp: str
    transaction_amount: float


# Load the pickled model
try:
    with open("lr_model.pkl", "rb") as file:
        model = pickle.load(file)
    logger.info("Model loaded successfully from pickle file")
except FileNotFoundError:
    logger.error(
        "Model file not found. Ensure 'fraud_detection_model.pkl' exists in the current directory"
    )
    raise
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Fraud Detection API")


@app.get("/")
async def root():
    return {
        "message": "Credit Card Fraud Detection API",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: Transaction):
    try:
        # Convert transaction to DataFrame
        features = pd.DataFrame([transaction.dict()])

        # Ensure correct column order
        columns = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
        features = features[columns]

        # Make prediction
        probability = model.predict_proba(features)[0][1]
        prediction = int(probability >= 0.5)

        response = PredictionResponse(
            prediction=prediction,
            probability=float(probability),
            timestamp=datetime.now().isoformat(),
            transaction_amount=transaction.Amount,
        )

        # Log the prediction
        logger.info(
            f"Prediction made - Amount: {transaction.Amount}, "
            f"Prediction: {prediction}, Probability: {probability:.4f}"
        )

        return response

    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error making prediction: {str(e)}"
        )


@app.get("/model-info")
async def model_info():
    """Return information about the loaded model"""
    try:
        return {
            "model_type": type(model).__name__,
            "features": len(model.feature_names_in_)
            if hasattr(model, "feature_names_in_")
            else None,
            "last_loaded": datetime.now().isoformat(),
            "sklearn_version": getattr(model, "_sklearn_version", "unknown"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
