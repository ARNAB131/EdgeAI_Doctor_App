class DigitalTwinManager:
    """Manages the digital twin for each patient."""

    def __init__(self, predictor, data_manager):
        self.predictor = predictor
        self.data_manager = data_manager
        self.twins = {}

    def update_twin(self, patient_id, vitals, predictions=None):
        """Store vitals and predictions in digital twin."""
        self.twins[patient_id] = {
            "vitals": vitals,
            "predictions": predictions or []
        }

    def get_twin(self, patient_id):
        """Retrieve patient twin."""
        return self.twins.get(patient_id, {})

    def get_all_twins_summary(self):
        """Return summary for all patients."""
        total_patients = len(self.twins)
        high_risk = [
            pid for pid, twin in self.twins.items()
            if any(
                isinstance(pred, dict) and pred.get("risk") == "high"
                for pred in twin.get("predictions", [])
            )
        ]
        return {
            "total_patients": total_patients,
            "high_risk_patients": high_risk
        }
