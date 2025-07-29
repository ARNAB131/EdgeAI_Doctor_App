class AlertManager:
    """Handles alerts for abnormal vitals."""

    def __init__(self, config, data_manager):
        self.config = config
        self.data_manager = data_manager
        self.thresholds = {
            "heart_rate": (60, 100),
            "bp_systolic": (90, 120),
            "bp_diastolic": (60, 80),
            "oxygen_saturation": (95, 100),
            "temperature": (36.1, 37.5)
        }
        self.alerts = {}

    def generate_alert(self, patient_id, twin, predictions):
        alerts = []
        vitals = twin.get("vitals", [])

        # Check vitals
        for vital in vitals:
            if hasattr(vital, "sensor_type"):
                sensor = vital.sensor_type.lower()
                if sensor in self.thresholds:
                    low, high = self.thresholds[sensor]
                    if vital.value < low or vital.value > high:
                        alert_msg = f"{sensor.capitalize()} out of range: {vital.value}"
                        alerts.append(alert_msg)

        # Store alerts
        if alerts:
            self.alerts[patient_id] = alerts
            return {
                "title": "🚨 Alert",
                "message": "\n".join(alerts)
            }
        return None

    def get_alert_statistics(self):
        return {
            "active_alerts": len(self.alerts)
        }
