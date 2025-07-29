class DigitalTwinManager:
    """Simulates a patient digital twin"""

    def __init__(self):
        self.twins = {}

    def update_twin(self, patient_id, vitals):
        self.twins[patient_id] = vitals

    def get_twin(self, patient_id):
        return self.twins.get(patient_id, {})
