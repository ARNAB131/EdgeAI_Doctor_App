import random

class SimulatedECGSensor:
    """Simulates an ECG sensor reading heart rate."""
    def read(self):
        return {
            "heart_rate": random.randint(60, 100)
        }

