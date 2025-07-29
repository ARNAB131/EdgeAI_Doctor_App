class ProductionConfig:
    """Safe configuration for Edge AI Doctor App."""

    def __init__(self, model_path="models/model.pkl", data_path="data/vitals.csv", update_interval=10):
        """
        Initialize the configuration with safe default values.
        
        :param model_path: Path to the model file.
        :param data_path: Path to the vitals data CSV.
        :param update_interval: Time interval for updates (in seconds).
        """
        self.model_path = model_path
        self.data_path = data_path
        self.update_interval = update_interval

    def get_config(self):
        """Return config details as a dictionary."""
        return {
            "model_path": self.model_path,
            "data_path": self.data_path,
            "update_interval": self.update_interval
        }

