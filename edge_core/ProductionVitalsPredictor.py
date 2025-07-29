import os
import pickle
import pandas as pd

class ProductionVitalsPredictor:
    """Predicts patient vitals trends from history."""

    def __init__(self, config):
        model_path = config.model_path

        # Load model if available
        if not os.path.exists(model_path):
            print(f"⚠️ Model file missing at {model_path}, using dummy model")
            self.model = None
        else:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

        # Define the required feature order
        self.required_features = [
            "heart_rate",
            "bp_systolic",
            "bp_diastolic",
            "oxygen_saturation",
            "temperature"
        ]

    def predict(self, features_df: pd.DataFrame):
        """Make prediction using model or dummy output if model is missing."""
        # Ensure all required columns are present
        for col in self.required_features:
            if col not in features_df.columns:
                features_df[col] = 0

        # Correct column order
        features_df = features_df[self.required_features]
        features_df = features_df.fillna(0)

        if self.model is None:
            # Dummy prediction to avoid crashing
            return [0] * len(features_df)
        return self.model.predict(features_df)

    def predict_trend(self, patient_id, history):
        """Predict future trend from patient's vitals history."""
        if not history:
            return None

        df = pd.DataFrame(history)

        # Start with default values
        features = {
            "heart_rate": 70,
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "oxygen_saturation": 98,
            "temperature": 36.5
        }

        # Update from recent history if available
        try:
            hr = pd.to_numeric(df[df["sensor"].isin(["ECG", "heart_rate"])]["value"], errors="coerce").dropna()
            if not hr.empty:
                features["heart_rate"] = hr.iloc[-1]
        except Exception:
            pass

        try:
            bp_values = df[df["sensor"].isin(["BP_SYS", "BP", "blood_pressure"])]["value"].dropna()
            if not bp_values.empty and "/" in str(bp_values.iloc[-1]):
                sys_val, dia_val = bp_values.iloc[-1].split("/")
                features["bp_systolic"] = pd.to_numeric(sys_val, errors="coerce")
                features["bp_diastolic"] = pd.to_numeric(dia_val, errors="coerce")
        except Exception:
            pass

        try:
            spo2 = pd.to_numeric(df[df["sensor"].isin(["SpO2", "oxygen_saturation"])]["value"], errors="coerce").dropna()
            if not spo2.empty:
                features["oxygen_saturation"] = spo2.iloc[-1]
        except Exception:
            pass

        try:
            temp = pd.to_numeric(df[df["sensor"].isin(["Temp", "temperature"])]["value"], errors="coerce").dropna()
            if not temp.empty:
                features["temperature"] = temp.iloc[-1]
        except Exception:
            pass

        # Convert features to DataFrame
        feature_df = pd.DataFrame([features])

        # Predict
        y_pred = self.predict(feature_df)

        return {
            "prediction_type": "Vitals Trend",
            "predicted_value": float(y_pred[0]) if len(y_pred) else 0,
            "confidence": 0.85 if self.model else 0.5,
            "uncertainty": 0.15 if self.model else 0.5,
            "risk_factors": [],
            "risk": "high" if y_pred[0] > 150 else "normal"
        }
