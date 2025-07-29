import random
import asyncio
from datetime import datetime

class SimulatedBloodPressureMonitor:
    """Simulates Blood Pressure readings (systolic & diastolic)"""
    def __init__(self, patient_id, device_id):
        self.patient_id = patient_id
        self.device_id = device_id

    async def read_data(self):
        await asyncio.sleep(0.5)
        systolic_value = random.randint(110, 140)
        diastolic_value = random.randint(70, 90)

        return [
            {
                "patient_id": self.patient_id,
                "device_id": self.device_id,
                "sensor_type": "BP_SYS",
                "value": systolic_value,
                "unit": "mmHg",
                "timestamp": datetime.now(),
                "quality_score": random.uniform(0.9, 1.0)
            },
            {
                "patient_id": self.patient_id,
                "device_id": self.device_id,
                "sensor_type": "BP_DIA",
                "value": diastolic_value,
                "unit": "mmHg",
                "timestamp": datetime.now(),
                "quality_score": random.uniform(0.9, 1.0)
            }
        ]
