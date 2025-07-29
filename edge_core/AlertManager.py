class AlertManager:
    def __init__(self, config, data_manager):
        self.config = config
        self.data_manager = data_manager
        # Map sensor names to expected ranges
        self.thresholds = {
            "ecg": (60, 100),  # bpm
            "bp_systolic": (90, 120),
            "bp_diastolic": (60, 80),
            "spo2": (95, 100),  # %
            "temp": (36.1, 37.5)  # °C
        }
        self.alerts = {}

    def generate_alert(self, patient_id, twin, predictions):
        alerts = []
        vitals = twin.get("vitals", [])

        for vital in vitals:
            # Extract sensor type + value from dict or object
            sensor_type = getattr(vital, "sensor_type", vital.get("sensor_type", "")).lower()
            value = getattr(vital, "value", vital.get("value", None))

            # Special handling for BP in "120/80" format
            if sensor_type in ["bp", "blood_pressure"] and isinstance(value, str) and "/" in value:
                try:
                    sys_val, dia_val = map(int, value.split("/"))
                    if sys_val < self.thresholds["bp_systolic"][0] or sys_val > self.thresholds["bp_systolic"][1]:
                        alerts.append(f"Systolic BP out of range: {sys_val}")
                    if dia_val < self.thresholds["bp_diastolic"][0] or dia_val > self.thresholds["bp_diastolic"][1]:
                        alerts.append(f"Diastolic BP out of range: {dia_val}")
                except ValueError:
                    pass
            else:
                # Normal vital check
                if sensor_type in self.thresholds and value is not None:
                    low, high = self.thresholds[sensor_type]
                    try:
                        if float(value) < low or float(value) > high:
                            alerts.append(f"{sensor_type.capitalize()} out of range: {value}")
                    except ValueError:
                        pass

        # Store alerts for this patient
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
