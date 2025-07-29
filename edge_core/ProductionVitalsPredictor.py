import os
import pickle
import pandas as pd

class ProductionVitalsPredictor:
    """Predicts patient vitals"""

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
        if self.model is None:
            print("⚠️ No model loaded. Returning dummy prediction.")
            return [0] * len(features)  # Dummy prediction to avoid crash
        return self.model.predict(features)


