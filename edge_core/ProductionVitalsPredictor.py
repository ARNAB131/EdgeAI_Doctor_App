import os
import pickle
import pandas as pd
import streamlit as st  # For debug logging in Cloud

class ProductionVitalsPredictor:
    """Predicts patient vitals trends"""

    def __init__(self, config):
        model_path = config.model_path

        # Ensure absolute path
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, model_path)

        # Load model safely
        self.model = None
        self.feature_names = []

        if not os.path.exists(model_path):
            st.warning(f"⚠️ Model file not found at {model_path}. Using fallback model.")
        else:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
                if hasattr(self.model, "feature_names_in_"):
                    self.feature_names = list(self.model.feature_names_in_)
                else:
                    # Define fallback
                    self.feature_names = ["heart_rate", "bp_systolic", "bp_diastolic", "oxygen_saturation", "temperature"]

    def _prepare_features(self, df: pd.DataFrame):
        """Ensure DataFrame matches exactly model expected features."""
        safe_df = pd.DataFrame(columns=self.feature_names)

        for col in self.feature_names:
            safe_df[col] = df[col] if col in df.columns else 0

        safe_df = safe_df[self.feature_names]

        # Debug: Show aligned columns in Streamlit logs
        st.write("📊 Model Input Columns:", list(safe_df.columns))
        st.write("📈 Model Input Values:", safe_df.tail(1).to_dict(orient="records"))

        return safe_df

    def predict(self, features: pd.DataFrame):
        """Predict from features aligned with model."""
        if self.model is None:
            st.warning("⚠️ No model loaded. Returning dummy prediction.")
            return [0] * len(features)

        safe_features = self._prepare_features(features)
        return self.model.predict(safe_features)

def predict_trend(self, patient_id, history):
    """Predict trend for patient based on recent history."""
    if not history:
        return None

    df_history = pd.DataFrame(history)

    # Convert sensor readings to wide format
    if "sensor" in df_history.columns:
        df_pivot = df_history.pivot_table(
            index="patient_id", 
            columns="sensor", 
            values="value", 
            aggfunc="last"
        ).reset_index()
    else:
        df_pivot = df_history.copy()

    # Rename to match model feature names
    rename_map = {
        "ECG": "heart_rate",
        "BP_SYS": "bp_systolic",
        "BP_DIA": "bp_diastolic",
        "SpO2": "oxygen_saturation",
        "Temp": "temperature"
    }
    df_pivot.rename(columns=rename_map, inplace=True)

    numeric_df = df_pivot.select_dtypes(include="number")

    # If still empty, fallback to zeros
    if numeric_df.empty:
        numeric_df = pd.DataFrame([{
            "heart_rate": 0,
            "bp_systolic": 0,
            "bp_diastolic": 0,
            "oxygen_saturation": 0,
            "temperature": 0
        }])

    prediction_value = self.predict(numeric_df)
    risk_level = "high" if prediction_value[0] > 100 else "normal"

    return {
        "patient_id": patient_id,
        "prediction_type": "trend",
        "predicted_value": float(prediction_value[0]),
        "confidence": 0.85,
        "risk": risk_level
    }
