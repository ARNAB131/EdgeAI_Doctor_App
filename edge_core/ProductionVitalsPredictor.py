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
        if not os.path.exists(model_path):
            print(f"⚠️ Model file not found at {model_path}. Using fallback model.")
            self.model = None
        else:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

    def predict(self, features: pd.DataFrame):
        """Generic prediction."""
        if self.model is None:
            print("⚠️ No model loaded. Returning dummy prediction.")
            return [0] * len(features)
        return self.model.predict(features)

    def predict_trend(self, patient_id, history):
        """Predict trend based on patient history."""
        if not history:
            return None

        # Convert history to DataFrame
        df_history = pd.DataFrame(history)
        
        # Select numeric values
        numeric_df = df_history.select_dtypes(include="number")

        if numeric_df.empty:
            print(f"⚠️ No numeric data found for patient {patient_id}")
            return None

        prediction_value = self.predict(numeric_df.tail(1))

        # Determine risk level
        risk_level = "high" if prediction_value[0] > 100 else "normal"

        return {
            "patient_id": patient_id,
            "prediction_type": "trend",
            "predicted_value": float(prediction_value[0]),
            "confidence": 0.85,  # Dummy confidence for now
            "risk": risk_level
        }


