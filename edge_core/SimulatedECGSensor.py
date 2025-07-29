import random
import time

class SimulatedECGSensor:
    """Simulates an ECG sensor reading heart rate."""
    def read(self):
        return {
            "heart_rate": random.randint(60, 100)
        }

class SimulatedPulseOximeter:
    """Simulates a pulse oximeter reading oxygen saturation."""
    def read(self):
        return {
            "oxygen_saturation": round(random.uniform(95, 100), 1)
        }

class SimulatedBloodPressureMonitor:
    """Simulates a blood pressure monitor reading systolic and diastolic BP."""
    def read(self):
        return {
            "bp_systolic": random.randint(110, 130),
            "bp_diastolic": random.randint(70, 85)
        }
