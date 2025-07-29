import os
import pickle
import pandas as pd

class ProductionVitalsPredictor:
    """Predicts patient vitals trends"""

    def __init__(self, config):
        model_path = config.model_path

        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, model_path)

        if not os.path.exists(model_path):
            print(f"⚠️ Model file not found at {model_path}. Using fallback.")
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
        """Make prediction using model or dummy"""
        # Ensure all required columns are present in correct order
        for col in self.required_features:
            if col not in features_df.columns:
                features_df[col] = 0  # Add missing column as 0

        features_df = features_df[self.required_features]  # Correct order
        features_df = features_df.fillna(0)

        if self.model is None:
            return [0] * len(features_df)  # Dummy output
        return self.model.predict(features_df)

    def predict_trend(self, patient_id, history):
        """Predict future trend from vitals history"""
        if not history:
            return None

        df = pd.DataFrame(history)

        numeric_df = pd.DataFrame({
            "heart_rate": pd.to_numeric(df[df["sensor"] == "ECG"]["value"], errors="coerce").tail(1).fillna(0),
            "bp_systolic": pd.to_numeric(df[df["sensor"].isin(["BP_SYS", "BP"])]["value"].apply(
                lambda x: str(x).split("/")[0] if "/" in str(x) else x
            ), errors="coerce").tail(1).fillna(0),
            "bp_diastolic": pd.to_numeric(df[df["sensor"].isin(["BP_DIA", "BP"])]["value"].apply(
                lambda x: str(x).split("/")[1] if "/" in str(x) else x
            ), errors="coerce").tail(1).fillna(0),
            "oxygen_saturation": pd.to_numeric(df[df["sensor"] == "SpO2"]["value"], errors="coerce").tail(1).fillna(0),
            "temperature": pd.Series([36.5])  # Placeholder
        })

        numeric_df = numeric_df.fillna(0)

        y_pred = self.predict(numeric_df)

        return {
            "prediction_type": "Vitals Trend",
            "predicted_value": float(y_pred[0]) if len(y_pred) else 0,
            "confidence": 0.85,
            "uncertainty": 0.15,
            "risk_factors": []
        }
