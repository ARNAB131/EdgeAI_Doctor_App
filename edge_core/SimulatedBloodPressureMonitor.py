import random

class SimulatedBloodPressureMonitor:
    """Simulates a blood pressure monitor reading systolic and diastolic BP."""
    
    def read(self):
        return {
            "bp_systolic": random.randint(110, 130),
            "bp_diastolic": random.randint(70, 85)
        }
