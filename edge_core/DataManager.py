import pandas as pd
import os
from datetime import datetime

class DataManager:
    """Handles data loading, saving, and vital history."""

    def __init__(self, config):
        self.data_path = config.data_path
        self.vitals_history = {}  # In-memory cache

        # Define consistent ML model input features
        self.feature_columns = [
            "heart_rate",
            "bp_systolic",
            "bp_diastolic",
            "oxygen_saturation",
            "temperature"
        ]

        # ----------------------------
        # Ensure vitals.csv has a sensor column
        # ----------------------------
        if os.path.exists(self.data_path):
            try:
                df = pd.read_csv(self.data_path)
            except Exception:
                df = pd.DataFrame(columns=["patient_id", "timestamp"] + self.feature_columns + ["sensor"])

            if "sensor" not in df.columns:
                df["sensor"] = None
                for i, row in df.iterrows():
                    if pd.notnull(row.get("heart_rate")):
                        df.at[i, "sensor"] = "ECG"
                    elif pd.notnull(row.get("bp_systolic")):
                        df.at[i, "sensor"] = "BP_SYS"
                    elif pd.notnull(row.get("bp_diastolic")):
                        df.at[i, "sensor"] = "BP_DIA"
                    elif pd.notnull(row.get("oxygen_saturation")):
                        df.at[i, "sensor"] = "SpO2"
                    elif pd.notnull(row.get("temperature")):
                        df.at[i, "sensor"] = "Temp"

                df.to_csv(self.data_path, index=False)

    def load_data(self):
        """Load CSV data from file safely."""
        if os.path.exists(self.data_path):
            try:
                return pd.read_csv(self.data_path)
            except Exception:
                return pd.DataFrame(columns=["patient_id", "timestamp"] + self.feature_columns + ["sensor"])
        return pd.DataFrame(columns=["patient_id", "timestamp"] + self.feature_columns + ["sensor"])

    def save_data(self, df):
        """Save DataFrame to CSV."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        df.to_csv(self.data_path, index=False)

    def store_vital_sign(self, vital):
        """Store vitals in wide format for ML, and keep sensor info for plotting."""
        pid = getattr(vital, "patient_id", vital.get("patient_id"))
        timestamp = getattr(vital, "timestamp", vital.get("timestamp", datetime.now()))
        sensor_type = getattr(vital, "sensor_type", vital.get("sensor_type"))
        value = getattr(vital, "value", vital.get("value"))

        # Load existing data
        df = self.load_data()

        # Map sensor types to ML feature columns
        mapping = {
            "ECG": "heart_rate",
            "BP_SYS": "bp_systolic",
            "BP_DIA": "bp_diastolic",
            "SpO2": "oxygen_saturation",
            "Temp": "temperature"
        }
        feature_col = mapping.get(sensor_type)

        # Ensure sensor column exists
        if "sensor" not in df.columns:
            df["sensor"] = None

        if feature_col:
            # Update or create patient record
            if pid in df["patient_id"].values:
                idx = df[df["patient_id"] == pid].index[-1]
                df.at[idx, feature_col] = value
                df.at[idx, "timestamp"] = timestamp
                df.at[idx, "sensor"] = sensor_type
            else:
                new_row = {col: None for col in self.feature_columns}
                new_row["patient_id"] = pid
                new_row["timestamp"] = timestamp
                new_row["sensor"] = sensor_type
                new_row[feature_col] = value
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        self.save_data(df)

    def get_patient_vitals_history(self, patient_id, sensor_type=None, limit=30):
        """Retrieve last N vital readings for a patient."""
        df = self.load_data()
        patient_data = df[df["patient_id"] == patient_id]
        return patient_data.tail(limit).to_dict("records")

    def store_prediction(self, prediction):
        """Store predictions if needed in future."""
        pass
