import os

class ProductionConfig:
    """Handles configuration for model paths and data locations."""

    def __init__(self, model_path=None, data_path="data/vitals.csv", update_interval=10):
        # Resolve paths relative to project root
        base_dir = os.path.dirname(os.path.abspath(__file__))  # edge_core folder
        project_root = os.path.dirname(base_dir)  # Go up to project root

        self.model_path = model_path or os.path.join(project_root, "models", "model.pkl")
        self.data_path = os.path.join(project_root, data_path)
        self.update_interval = update_interval

    def get_config(self):
        """Return config details as a dictionary."""
        return {
            "model_path": self.model_path,
            "data_path": self.data_path,
            "update_interval": self.update_interval
        }
