import pickle
import pandas as pd

class ProductionConfig:
    """Safe configuration for Edge AI Doctor App."""

    def __init__(self, model_path="models/model.pkl", data_path="data/vitals.csv", update_interval=10):
        self.model_path = model_path
        self.data_path = data_path
        self.update_interval = update_interval

    def get_config(self):
        return {
            "model_path": self.model_path,
            "data_path": self.data_path,
            "update_interval": self.update_interval
        }
