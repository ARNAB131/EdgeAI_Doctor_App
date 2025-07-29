import pandas as pd
import os
from datetime import datetime

class DataManager:
    """Handles data loading, saving, and vital history."""

    def __init__(self, config):
        self.data_path = config.data_path
        self.vitals_history = {}  # In-memory cache

    def load_data(self):
        """Load CSV data from file."""
        if os.path.exists(self.data_path):
            try:
                return pd.read_csv(self.data_path)
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame()

    def save_data(self, df):
        """Save DataFrame to CSV."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        df.to_csv(self.data_path, index=False)

    def store_vital_sign(self, vital):
        """Store a single vital in memory + append to CSV."""
        # Support both object and dict input
        pid = getattr(vital, "patient_id", vital.get("patient_id"))
        timestamp = getattr(vital, "timestamp", vital.get("timestamp", datetime.now()))
        sensor_type = getattr(vital, "sensor_type", vital.get("sensor_type"))
        value = getattr(vital, "value", vital.get("value"))
        unit = getattr(vital, "unit", vital.get("unit"))
        quality_score = getattr(vital, "quality_score", vital.get("quality_score", 1.0))

        # Store in in-memory cache
        if pid not in self.vitals_history:
            self.vitals_history[pid] = []
        self.vitals_history[pid].append(vital)

        # Append to CSV
        df = self.load_data()
        df_new = pd.DataFrame([{
            "patient_id": pid,
            "timestamp": timestamp,
            "sensor": sensor_type,
            "value": value,
            "unit": unit,
            "quality_score": quality_score
        }])
        df = pd.concat([df, df_new], ignore_index=True)
        self.save_data(df)

    def get_patient_vitals_history(self, patient_id, sensor_type=None, limit=30):
        """Retrieve last N vital readings for a patient."""
        df = self.load_data()
        patient_data = df[df["patient_id"] == patient_id]
        if sensor_type:
            patient_data = patient_data[patient_data["sensor"] == sensor_type]
        return patient_data.tail(limit).to_dict("records")

    def store_prediction(self, prediction):
        """Optionally store predictions (extend later)."""
        # Future: Save prediction data alongside vitals
        pass
