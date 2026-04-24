"""
Auto Predict Script - Signé SOLITAIRE HACK 🇨🇮
Prédictions automatiques continues sur les données Crash
"""

import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import time
import json
import os

MODEL_PATH = "crash_ai_model.joblib"
CSV_PATH = "TRAIN-666.CSV"


def extract_time_features(timestamp_str: str) -> tuple:
    """Extract hour, minute, second from ISO timestamp"""
    try:
        if pd.isna(timestamp_str) or timestamp_str == "":
            return 0, 0, 0
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
    
    return df


def load_model():
    """Load trained model from disk"""
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def predict_on_csv():
    """Make predictions on all valid rows in CSV"""
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found. Train the model first.")
        return None
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV not found: {CSV_PATH}")
        return None
    
    # Load model
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded")
    
    # Read and prepare data
    df = pd.read_csv(CSV_PATH)
    df = prepare_features(df)
    
    # Drop rows with NaN in features
    feature_cols = ["hour", "minute", "second", "prev_1", "prev_2", "prev_3", 
                    "avg_5", "low_count_5", "high_count_10"]
    df_clean = df.dropna(subset=feature_cols)
    
    print(f"📊 {len(df_clean)} rows ready for prediction")
    
    # Make predictions
    X = df_clean[feature_cols]
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    confidences = np.max(probabilities, axis=1)
    
    # Add predictions to dataframe
    df_clean["prediction"] = predictions
    df_clean["confidence"] = confidences
    
    # Generate signals
    def get_signal(row):
        if row["prediction"] == 1 and row["confidence"] >= 0.7:
            return "ENTRÉE PRUDENTE"
        elif row["prediction"] == 1 and row["confidence"] < 0.7:
            return "ENTRÉE TRÈS PRUDENTE"
        else:
            return "ATTENDRE"
    
    df_clean["signal"] = df_clean.apply(get_signal, axis=1)
    
    # Select columns to display
    result_cols = ["timestamp_iso", "value", "prediction", "confidence", "signal"]
    results = df_clean[result_cols]
    
    return results


def predict_next(last_values: list):
    """Predict next crash based on last values"""
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found. Train the model first.")
        return None
    
    model = joblib.load(MODEL_PATH)
    
    # Get current time
    now = datetime.now()
    
    # Calculate features
    if len(last_values) < 3:
        print("❌ Need at least 3 previous values")
        return None
    
    prev_1 = last_values[0]
    prev_2 = last_values[1]
    prev_3 = last_values[2]
    
    # Calculate rolling features
    if len(last_values) >= 5:
        avg_5 = np.mean(last_values[:5])
        low_count_5 = sum(1 for v in last_values[:5] if v < 2.0)
    else:
        avg_5 = np.mean(last_values)
        low_count_5 = sum(1 for v in last_values if v < 2.0)
    
    if len(last_values) >= 10:
        high_count_10 = sum(1 for v in last_values[:10] if v >= 2.0)
    else:
        high_count_10 = sum(1 for v in last_values if v >= 2.0)
    
    # Prepare features
    features = np.array([[
        now.hour,
        now.minute,
        now.second,
        prev_1,
        prev_2,
        prev_3,
        avg_5,
        low_count_5,
        high_count_10
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
    
    result = {
        "timestamp": now.isoformat(),
        "prediction": int(prediction),
        "confidence": round(confidence, 4),
        "signal": signal,
        "features": {
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "prev_1": prev_1,
            "prev_2": prev_2,
            "prev_3": prev_3,
            "avg_5": avg_5,
            "low_count_5": low_count_5,
            "high_count_10": high_count_10
        }
    }
    
    return result


if __name__ == "__main__":
    
    print("=" * 60)
    print("🤖 CRASH AI - AUTO PREDICT")
    print("Signé SOLITAIRE HACK 🇨🇮")
    print("=" * 60)
    print()
    
    # Predict on entire CSV
    print("📊 Predictions on CSV data:")
    print("-" * 60)
    results = predict_on_csv()
    
    if results is not None:
        print(results.to_string(index=False))
        print()
        print(f"✅ Total predictions: {len(results)}")
        
        # Statistics
        print()
        print("📈 Statistics:")
        print(f"  - ENTRÉE PRUDENTE: {len(results[results['signal'] == 'ENTRÉE PRUDENTE'])}")
        print(f"  - ENTRÉE TRÈS PRUDENTE: {len(results[results['signal'] == 'ENTRÉE TRÈS PRUDENTE'])}")
        print(f"  - ATTENDRE: {len(results[results['signal'] == 'ATTENDRE'])}")
        print(f"  - Average confidence: {results['confidence'].mean():.4f}")
    
    print()
    print("-" * 60)
    print("💡 Example: Predict next crash with last values")
    print("-" * 60)
    
    # Example with last values from CSV
    example_values = [1.13, 2.72, 2.97, 1.71, 7.54]
    result = predict_next(example_values)
    
    if result:
        print(json.dumps(result, indent=2))
