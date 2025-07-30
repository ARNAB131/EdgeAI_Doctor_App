import pandas as pd
import os
from datetime import datetime

class DataManager:
    """Handles data loading, saving, and vital history."""

    def __init__(self, config):
        self.data_path = config.data_path
        self.vitals_history = {}
        self.feature_columns = ["heart_rate", "bp_systolic", "bp_diastolic", "oxygen_saturation", "temperature"]

        # Ensure CSV has correct columns
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            if "sensor" not in df.columns:
                df["sensor"] = None
            if "value" not in df.columns:
                df["value"] = None
            df.to_csv(self.data_path, index=False)

    def load_data(self):
        """Load CSV safely with required columns."""
        base_cols = ["patient_id", "timestamp", "sensor", "value"] + self.feature_columns
        if os.path.exists(self.data_path):
            try:
                df = pd.read_csv(self.data_path)
                for col in base_cols:
                    if col not in df.columns:
                        df[col] = None
                return df
            except Exception:
                return pd.DataFrame(columns=base_cols)
        return pd.DataFrame(columns=base_cols)

    def save_data(self, df):
        """Save DataFrame to CSV."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        df.to_csv(self.data_path, index=False)

    def store_vital_sign(self, vital):
        """Store vitals in wide + long format (value column for graphing)."""
        pid = getattr(vital, "patient_id", vital.get("patient_id"))
        timestamp = getattr(vital, "timestamp", vital.get("timestamp", datetime.now()))
        sensor_type = getattr(vital, "sensor_type", vital.get("sensor_type"))
        value = getattr(vital, "value", vital.get("value"))

        df = self.load_data()

        mapping = {
            "ECG": "heart_rate",
            "BP_SYS": "bp_systolic",
            "BP_DIA": "bp_diastolic",
            "SpO2": "oxygen_saturation",
            "Temp": "temperature"
        }
        feature_col = mapping.get(sensor_type)

        # Add or update row
        new_row = {col: None for col in self.feature_columns}
        new_row.update({
            "patient_id": pid,
            "timestamp": timestamp,
            "sensor": sensor_type,
            "value": value
        })
        if feature_col:
            new_row[feature_col] = value

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_data(df)

    def get_patient_vitals_history(self, patient_id, sensor_type=None, limit=30):
        """Get last N vitals."""
        df = self.load_data()
        patient_data = df[df["patient_id"] == patient_id]
        if sensor_type:
            patient_data = patient_data[patient_data["sensor"] == sensor_type]
        return patient_data.tail(limit).to_dict("records")

    def store_prediction(self, prediction):
        pass
