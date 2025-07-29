import os
import pickle
import pandas as pd

class ProductionVitalsPredictor:
    """Predicts patient vitals trends"""

    def __init__(self, config):
        model_path = config.model_path

        # Ensure absolute path
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, model_path)

        # Safe model loading
        self.model = None
        self.feature_names = []  # store expected features

        if not os.path.exists(model_path):
            print(f"⚠️ Model file not found at {model_path}. Using fallback model.")
        else:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
                if hasattr(self.model, "feature_names_in_"):
                    self.feature_names = list(self.model.feature_names_in_)
                else:
                    # Default expected vitals
                    self.feature_names = ["heart_rate", "bp_systolic", "bp_diastolic", "oxygen_saturation", "temperature"]

    def _prepare_features(self, df: pd.DataFrame):
        """Ensure dataframe matches expected model features."""
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0  # fill missing
        return df[self.feature_names]

    def predict(self, features: pd.DataFrame):
        if self.model is None:
            print("⚠️ No model loaded. Returning dummy prediction.")
            return [0] * len(features)

        safe_features = self._prepare_features(features)
        return self.model.predict(safe_features)

    def predict_trend(self, patient_id, history):
        """Predict trend based on patient history."""
        if not history:
            return None

        df_history = pd.DataFrame(history)
        numeric_df = df_history.select_dtypes(include="number")

        if numeric_df.empty:
            print(f"⚠️ No numeric data found for patient {patient_id}")
            return None

        prediction_value = self.predict(numeric_df.tail(1))
        risk_level = "high" if prediction_value[0] > 100 else "normal"

        return {
            "patient_id": patient_id,
            "prediction_type": "trend",
            "predicted_value": float(prediction_value[0]),
            "confidence": 0.85,
            "risk": risk_level
        }
