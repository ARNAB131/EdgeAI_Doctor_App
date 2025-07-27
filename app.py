#app.py
import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime
import plotly.graph_objs as go
from edge_core import ProductionConfig, DataManager, ProductionVitalsPredictor, DigitalTwinManager, AlertManager
from edge_core import SimulatedECGSensor, SimulatedPulseOximeter, SimulatedBloodPressureMonitor
from utils.auth import login
from utils.pdf_report import generate_pdf
from utils.cloud_sync import simulate_sync

# Setup
st.set_page_config("🧠 Doctigo Edge AI", layout="wide")
st.title("🩺 Real-Time Edge AI Patient Monitoring")

# Authenticate
if not login():
    st.stop()

# Load core managers
config = ProductionConfig()
data_manager = DataManager(config)
predictor = ProductionVitalsPredictor(config)
twin_manager = DigitalTwinManager(predictor, data_manager)
alert_manager = AlertManager(config, data_manager)

simulate_sync()  # Show cloud sync

# Patient and sensors
patient_id = "patient_001"
device_id = "edge_001"

ecg_sensor = SimulatedECGSensor(patient_id, device_id)
spo2_sensor = SimulatedPulseOximeter(patient_id, device_id)
bp_sensor = SimulatedBloodPressureMonitor(patient_id, device_id)

# Sidebar: sensor selector
st.sidebar.subheader("🎚️ Select Sensors")
use_ecg = st.sidebar.checkbox("ECG", True)
use_spo2 = st.sidebar.checkbox("SpO2", True)
use_bp = st.sidebar.checkbox("BP", True)

# CSV Upload
st.sidebar.subheader("📤 Upload Vitals CSV")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    df_uploaded = pd.read_csv(uploaded)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df_uploaded)

    # Optional: predict from uploaded CSV
    st.sidebar.markdown("✅ Predictions from upload coming soon...")

# Button: simulate vitals
if st.button("📈 Read Selected Sensors"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    vitals = []
    if use_ecg:
        ecg = loop.run_until_complete(ecg_sensor.read_data())
        vitals.append(ecg)
    if use_spo2:
        spo2 = loop.run_until_complete(spo2_sensor.read_data())
        vitals.append(spo2)
    if use_bp:
        bp = loop.run_until_complete(bp_sensor.read_data())
        vitals.append(bp)

    for v in vitals:
        data_manager.store_vital_sign(v)

    all_history = data_manager.get_patient_vitals_history(patient_id, limit=30)
    prediction = predictor.predict_trend(patient_id, all_history)

    if prediction:
        data_manager.store_prediction(prediction)

    predictions = [prediction] if prediction else []
    twin_manager.update_twin(patient_id, vitals, predictions)

    twin = twin_manager.get_twin(patient_id)
    alert = alert_manager.generate_alert(patient_id, twin, predictions)

    st.success("✅ Simulation, Prediction & Alert done.")

    st.subheader("📊 Current Vitals")
    for v in vitals:
        st.markdown(f"**{v.sensor_type}**: `{v.value:.2f} {v.unit}` | Quality: `{v.quality_score:.2f}`")

    if prediction:
        st.subheader("🔮 Prediction")
        st.markdown(f"**{prediction.prediction_type}** → `{prediction.predicted_value:.2f}` (Confidence: `{prediction.confidence:.2f}`)")

    if alert:
        st.subheader("🚨 Alert")
        st.error(f"{alert.title}\n\n{alert.message}")

    # Plot chart
    st.subheader("📈 Vitals Chart")
    for sensor in set([v.sensor_type for v in vitals]):
        history = data_manager.get_patient_vitals_history(patient_id, sensor, limit=30)
        if history:
            df = pd.DataFrame([{
                "timestamp": v.timestamp,
                "value": v.value
            } for v in history])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["timestamp"], y=df["value"], mode="lines+markers", name=sensor))
            fig.update_layout(title=sensor, xaxis_title="Time", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)

    # PDF/CSV download
    pdf_path = generate_pdf(vitals, prediction)
    with open(pdf_path, "rb") as f_pdf:
        st.download_button("📥 Download PDF Report", f_pdf, file_name=pdf_path.split("/")[-1])

    df_all = pd.DataFrame([v.__dict__ for v in vitals])
    st.download_button("📥 Download CSV", df_all.to_csv(index=False), "vitals.csv", "text/csv")

# Sidebar summary
st.sidebar.title("📋 Summary")
summary = twin_manager.get_all_twins_summary()
alerts = alert_manager.get_alert_statistics()
st.sidebar.metric("Total Patients", summary["total_patients"])
st.sidebar.metric("Active Alerts", alerts["active_alerts"])
st.sidebar.metric("High Risk", len(summary["high_risk_patients"]))
