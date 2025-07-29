import pandas as pd
import os

class DataManager:
    """Handles data loading and saving"""

    def __init__(self, data_path):
        self.data_path = data_path

    def load_data(self):
        if os.path.exists(self.data_path):
            return pd.read_csv(self.data_path)
        else:
            return pd.DataFrame()

    def save_data(self, df):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        df.to_csv(self.data_path, index=False)
