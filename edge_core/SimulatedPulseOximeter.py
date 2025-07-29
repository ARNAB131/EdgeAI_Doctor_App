import random
import asyncio
from datetime import datetime

class SimulatedPulseOximeter:
    """Simulates Pulse Oximeter readings"""
    def __init__(self, patient_id, device_id):
        self.patient_id = patient_id
        self.device_id = device_id
        self.sensor_type = "SpO2"

    async def read_data(self):
        await asyncio.sleep(0.5)
        return {
            "patient_id": self.patient_id,
            "device_id": self.device_id,
            "sensor_type": self.sensor_type,
            "value": random.uniform(95, 100),
            "unit": "%",
            "timestamp": datetime.now(),
            "quality_score": random.uniform(0.9, 1.0)
        }
