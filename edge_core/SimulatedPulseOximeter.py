import random

class SimulatedPulseOximeter:
    """Simulates a pulse oximeter reading oxygen saturation."""
    
    def read(self):
        return {
            "oxygen_saturation": round(random.uniform(95.0, 100.0), 1)
        }
