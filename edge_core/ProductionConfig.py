class ProductionConfig:
    """Configuration for Edge AI Doctor App"""

    def __init__(self):
        self.model_path = "models/model.pkl"
        self.data_path = "data/vitals.csv"
        self.update_interval = 10  # seconds

    def get_config(self):
        return {
            "model_path": self.model_path,
            "data_path": self.data_path,
            "update_interval": self.update_interval
        }
