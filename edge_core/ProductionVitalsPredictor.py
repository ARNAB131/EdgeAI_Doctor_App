import pickle
import pandas as pd

class ProductionVitalsPredictor:
    """Predicts patient vitals"""

    def __init__(self, model_path):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: pd.DataFrame):
        return self.model.predict(features)


