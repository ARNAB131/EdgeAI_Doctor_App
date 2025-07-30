import pandas as pd
import os
from datetime import datetime

class DataManager:
    """Handles data loading, saving, and vital history."""

    def __init__(self, config):
        self.data_path = config.data_path

        # In-memory cache
        self.vitals_history = {}

        # Consistent ML model features
        self.feature_columns = [
            "heart_rate", "bp_systolic", "bp_diastolic", "oxygen_saturation", "temperature"
        ]

        # Ensure CSV has required columns
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            if "sensor" not in df.columns:
                df["sensor"] = None
            if "value" not in df.columns:
                df["value"] = None
            df.to_csv(self.data_path, index=False)

    def load_data(self):
        """Load CSV data safely."""
        if os.path.exists(self.data_path):
            try:
                return pd.read_csv(self.data_path)
            except Exception:
                return pd.DataFrame(columns=["patient_id", "timestamp", "sensor", "value"] + self.feature_columns)
        return pd.DataFrame(columns=["patient_id", "timestamp", "sensor", "value"] + self.feature_columns)

    def save_data(self, df):
        """Save DataFrame to CSV."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        df.to_csv(self.data_path, index=False)

    def store_vital_sign(self, vital):
        """Store vitals in both wide-format for ML and 'value' for plotting."""
        pid = getattr(vital, "patient_id", vital.get("patient_id"))
        timestamp = getattr(vital, "timestamp", vital.get("timestamp", datetime.now()))
        sensor_type = getattr(vital, "sensor_type", vital.get("sensor_type"))
        value = getattr(vital, "value", vital.get("value"))

        df = self.load_data()

        # Map sensor types to feature columns
        mapping = {
            "ECG": "heart_rate",
            "BP_SYS": "bp_systolic",
            "BP_DIA": "bp_diastolic",
            "SpO2": "oxygen_saturation",
            "Temp": "temperature"
        }
        feature_col = mapping.get(sensor_type)

        # Ensure columns exist
        if "sensor" not in df.columns:
            df["sensor"] = None
        if "value" not in df.columns:
            df["value"] = None

        # Update or create patient row
        if feature_col:
            if pid in df["patient_id"].values:
                idx = df[df["patient_id"] == pid].index[-1]
                df.at[idx, feature_col] = value
                df.at[idx, "value"] = value        # ✅ For plotting
                df.at[idx, "timestamp"] = timestamp
                df.at[idx, "sensor"] = sensor_type
            else:
                new_row = {col: None for col in self.feature_columns}
                new_row["patient_id"] = pid
                new_row["timestamp"] = timestamp
                new_row["sensor"] = sensor_type
                new_row["value"] = value           # ✅ For plotting
                new_row[feature_col] = value
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        self.save_data(df)

    def get_patient_vitals_history(self, patient_id, sensor_type=None, limit=30):
        """Retrieve last N vital readings."""
        df = self.load_data()
        patient_data = df[df["patient_id"] == patient_id]
        if sensor_type:
            patient_data = patient_data[patient_data["sensor"] == sensor_type]
        return patient_data.tail(limit).to_dict("records")

    def store_prediction(self, prediction):
        """Future: Store predictions."""
        pass
