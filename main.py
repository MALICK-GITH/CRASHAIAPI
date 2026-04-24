"""
Crash AI API - Signé SOLITAIRE HACK 🇨🇮
IA statistique d'aide à l'analyse du jeu Crash
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime
from typing import Optional
import os

app = FastAPI(title="Crash AI API", version="1.0.0")

# CORS support for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Chrome extension
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

MODEL_PATH = "crash_ai_model.joblib"
CSV_PATH = "TRAIN-666.CSV"


class PredictionRequest(BaseModel):
    hour: int
    minute: int
    second: int
    prev_1: float
    prev_2: float
    prev_3: float
    avg_5: float
    low_count_5: int
    high_count_10: int


def extract_time_features(timestamp_str: str) -> tuple:
    """Extract hour, minute, second from ISO timestamp"""
    try:
        if pd.isna(timestamp_str) or timestamp_str == "":
            return 0, 0, 0
        # Parse ISO format: 2026-04-24T04:34:07.101Z
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.hour, dt.minute, dt.second
    except:
        return 0, 0, 0


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare ML features from raw data"""
    # Extract time features
    df[["hour", "minute", "second"]] = df["timestamp_iso"].apply(
        lambda x: pd.Series(extract_time_features(x))
    )
    
    # Convert value to float
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    # Drop rows with invalid values
    df = df.dropna(subset=["value"])
    
    # Sort by timestamp to ensure correct lag features
    df = df.sort_values("timestamp_iso").reset_index(drop=True)
    
    # Create lag features (previous values)
    df["prev_1"] = df["value"].shift(1)
    df["prev_2"] = df["value"].shift(2)
    df["prev_3"] = df["value"].shift(3)
    
    # Rolling average of last 5 values
    df["avg_5"] = df["value"].rolling(window=5, min_periods=1).mean()
    
    # Count low values (< 2.0) in last 5 rounds
    df["low_count_5"] = df["value"].rolling(window=5, min_periods=1).apply(
        lambda x: (x < 2.0).sum(), raw=False
    )
    
    # Count high values (>= 2.0) in last 10 rounds
    df["high_count_10"] = df["value"].rolling(window=10, min_periods=1).apply(
        lambda x: (x >= 2.0).sum(), raw=False
    )
    
    # Create target
    df["target"] = (df["value"] >= 2.0).astype(int)
    
    # Drop rows with NaN in features (due to lag)
    feature_cols = ["hour", "minute", "second", "prev_1", "prev_2", "prev_3", 
                    "avg_5", "low_count_5", "high_count_10", "target"]
    df = df.dropna(subset=feature_cols)
    
    return df


def train_model():
    """Train RandomForestClassifier on CSV data"""
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
    
    # Read CSV
    df = pd.read_csv(CSV_PATH)
    
    # Prepare features
    df = prepare_features(df)
    
    if len(df) < 10:
        raise ValueError("Not enough valid data rows for training")
    
    # Define features and target
    feature_cols = ["hour", "minute", "second", "prev_1", "prev_2", "prev_3", 
                    "avg_5", "low_count_5", "high_count_10"]
    X = df[feature_cols]
    y = df["target"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model
    joblib.dump(model, MODEL_PATH)
    
    return len(df), accuracy


def load_model():
    """Load trained model from disk"""
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


@app.get("/")
def root():
    """Root endpoint - API status"""
    return {
        "status": "Crash AI API running",
        "project": "SOLITAIRE HACK 🇨🇮"
    }


@app.post("/train")
def train_endpoint():
    """Train the model on CSV data"""
    try:
        rows_used, accuracy = train_model()
        return {
            "status": "training_completed",
            "rows_used": rows_used,
            "model_file": MODEL_PATH,
            "accuracy": round(accuracy, 4)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


@app.post("/predict")
def predict_endpoint(request: PredictionRequest):
    """Make prediction using trained model"""
    model = load_model()
    
    if model is None:
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Call /train first."
        )
    
    try:
        # Prepare features
        features = np.array([[
            request.hour,
            request.minute,
            request.second,
            request.prev_1,
            request.prev_2,
            request.prev_3,
            request.avg_5,
            request.low_count_5,
            request.high_count_10
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities)
        
        # Generate signal
        if prediction == 1 and confidence >= 0.7:
            signal = "ENTRÉE PRUDENTE"
        elif prediction == 1 and confidence < 0.7:
            signal = "ENTRÉE TRÈS PRUDENTE"
        else:
            signal = "ATTENDRE"
        
        return {
            "prediction": int(prediction),
            "confidence": round(confidence, 4),
            "signal": signal
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict-batch")
def predict_batch_endpoint():
    """Make predictions on all valid rows in CSV"""
    model = load_model()
    
    if model is None:
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Call /train first."
        )
    
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail=f"CSV file not found: {CSV_PATH}")
    
    try:
        # Read and prepare data
        df = pd.read_csv(CSV_PATH)
        df = prepare_features(df)
        
        # Define features
        feature_cols = ["hour", "minute", "second", "prev_1", "prev_2", "prev_3", 
                        "avg_5", "low_count_5", "high_count_10"]
        X = df[feature_cols]
        
        # Make predictions
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        confidences = np.max(probabilities, axis=1)
        
        # Generate signals
        def get_signal(pred, conf):
            if pred == 1 and conf >= 0.7:
                return "ENTRÉE PRUDENTE"
            elif pred == 1 and conf < 0.7:
                return "ENTRÉE TRÈS PRUDENTE"
            else:
                return "ATTENDRE"
        
        # Build results
        results = []
        for i in range(len(df)):
            results.append({
                "timestamp_iso": df.iloc[i]["timestamp_iso"],
                "value": float(df.iloc[i]["value"]),
                "prediction": int(predictions[i]),
                "confidence": round(float(confidences[i]), 4),
                "signal": get_signal(predictions[i], confidences[i])
            })
        
        # Statistics
        signal_counts = {"ENTRÉE PRUDENTE": 0, "ENTRÉE TRÈS PRUDENTE": 0, "ATTENDRE": 0}
        for r in results:
            signal_counts[r["signal"]] += 1
        
        return {
            "total_predictions": len(results),
            "statistics": signal_counts,
            "average_confidence": round(float(np.mean(confidences)), 4),
            "predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
