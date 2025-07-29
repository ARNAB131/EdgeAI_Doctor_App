class AlertManager:
    """Handles alerts for abnormal vitals"""

    def __init__(self):
        self.thresholds = {
            "heart_rate": (60, 100),
            "bp_systolic": (90, 120),
            "bp_diastolic": (60, 80),
            "oxygen_saturation": (95, 100),
            "temperature": (36.1, 37.5)
        }

    def check_alerts(self, vitals):
        alerts = []
        for vital, (low, high) in self.thresholds.items():
            value = vitals.get(vital)
            if value is not None and (value < low or value > high):
                alerts.append(f"{vital} out of range: {value}")
        return alerts
