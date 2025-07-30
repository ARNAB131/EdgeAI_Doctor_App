# app.py
import streamlit as st
import pandas as pd
import asyncio
import time
from datetime import datetime
import plotly.graph_objs as go
from edge_core import ProductionConfig
from edge_core import DataManager, ProductionVitalsPredictor, DigitalTwinManager, AlertManager
from edge_core import SimulatedECGSensor, SimulatedPulseOximeter, SimulatedBloodPressureMonitor
from utils.auth import login
from utils.pdf_report import generate_pdf
from utils.cloud_sync import simulate_sync

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config("🧠 Doctigo Edge AI", layout="wide")
st.title("🩺 Real-Time Edge AI Patient Monitoring")

# --------------------------
# AUTHENTICATION
# --------------------------
if not login():
    st.stop()

# --------------------------
# CORE MANAGERS
# --------------------------
config = ProductionConfig()
data_manager = DataManager(config)
predictor = ProductionVitalsPredictor(config)
twin_manager = DigitalTwinManager(predictor, data_manager)
alert_manager = AlertManager(config, data_manager)

simulate_sync()  # Simulate cloud sync

# --------------------------
# PATIENT & DEVICES
# --------------------------
patient_id = "patient_001"
device_id = "edge_001"

ecg_sensor = SimulatedECGSensor(patient_id, device_id)
spo2_sensor = SimulatedPulseOximeter(patient_id, device_id)
bp_sensor = SimulatedBloodPressureMonitor(patient_id, device_id)

# Always define vitals
vitals = []

# --------------------------
# SIDEBAR - SENSOR SELECTION
# --------------------------
st.sidebar.subheader("🎚️ Select Sensors")
use_ecg = st.sidebar.checkbox("ECG", True)
use_spo2 = st.sidebar.checkbox("SpO2", True)
use_bp = st.sidebar.checkbox("BP", True)

# --------------------------
# SIDEBAR - COLOR LEGEND
# --------------------------
st.sidebar.markdown("### 🎨 Vitals Color Legend")

legend_html = """
<div style='display: flex; flex-direction: column; font-size: 14px;'>
    <div style='margin-bottom: 4px;'>
        <span style='background-color: red; width: 12px; height: 12px; display: inline-block; margin-right: 8px;'></span>
        ECG
    </div>
    <div style='margin-bottom: 4px;'>
        <span style='background-color: blue; width: 12px; height: 12px; display: inline-block; margin-right: 8px;'></span>
        SpO2
    </div>
    <div style='margin-bottom: 4px;'>
        <span style='background-color: green; width: 12px; height: 12px; display: inline-block; margin-right: 8px;'></span>
        BP_SYS
    </div>
    <div style='margin-bottom: 4px;'>
        <span style='background-color: orange; width: 12px; height: 12px; display: inline-block; margin-right: 8px;'></span>
        BP_DIA
    </div>
</div>
"""

st.sidebar.markdown(legend_html, unsafe_allow_html=True)

# --------------------------
# SIDEBAR - CSV UPLOAD WITH PREDICTION
# --------------------------
st.sidebar.subheader("📤 Upload Vitals CSV")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    df_uploaded = pd.read_csv(uploaded)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df_uploaded)

    try:
        df_for_pred = df_uploaded.copy()
        cols_to_keep = predictor.required_features
        df_for_pred = df_for_pred[[col for col in cols_to_keep if col in df_for_pred.columns]]

        for col in predictor.required_features:
            if col not in df_for_pred.columns:
                df_for_pred[col] = 0

        df_for_pred = df_for_pred.apply(pd.to_numeric, errors="coerce").fillna(0)
        csv_predictions = predictor.predict(df_for_pred)
        df_uploaded["Prediction"] = csv_predictions

        st.subheader("🔮 Predictions from Uploaded Data")
        st.dataframe(df_uploaded)

        st.download_button(
            "📥 Download Predictions CSV",
            df_uploaded.to_csv(index=False),
            file_name="predictions.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")

# --------------------------
# SIMULATE VITALS
# --------------------------
if st.button("📈 Read Selected Sensors"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if use_ecg:
        vitals.append(loop.run_until_complete(ecg_sensor.read_data()))
    if use_spo2:
        vitals.append(loop.run_until_complete(spo2_sensor.read_data()))
    if use_bp:
        bp_readings = loop.run_until_complete(bp_sensor.read_data())
        vitals.extend(bp_readings if isinstance(bp_readings, list) else [bp_readings])

    for v in vitals:
        data_manager.store_vital_sign(v)

    all_history = data_manager.get_patient_vitals_history(patient_id, limit=30)
    prediction = predictor.predict_trend(patient_id, all_history)
    predictions = [prediction] if prediction else []
    twin_manager.update_twin(patient_id, vitals, predictions)
    alert = alert_manager.generate_alert(patient_id, twin_manager.get_twin(patient_id), predictions)

    st.success("✅ Simulation, Prediction & Alert done.")

# --------------------------
# LIVE MULTI-SENSOR GRAPH (Always uses value column) - Colored
# --------------------------
import time

st.subheader("📡 Live Vitals Monitoring")
auto_refresh = st.checkbox("Enable Auto Mode", value=True)
refresh_rate = st.slider("Refresh Interval (seconds)", 1, 10, 3)

graph_placeholder = st.empty()

# Assign distinct colors for each sensor
sensor_colors = {
    "ECG": "red",         # Red for heart activity
    "SpO2": "blue",       # Blue for oxygen
    "BP_SYS": "green",    # Green for systolic BP
    "BP_DIA": "orange"    # Orange for diastolic BP
}

if auto_refresh:
    for _ in range(200):  # Safety loop limit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        vitals = []

        if use_ecg:
            vitals.append(loop.run_until_complete(ecg_sensor.read_data()))
        if use_spo2:
            vitals.append(loop.run_until_complete(spo2_sensor.read_data()))
        if use_bp:
            bp_readings = loop.run_until_complete(bp_sensor.read_data())
            vitals.extend(bp_readings if isinstance(bp_readings, list) else [bp_readings])

        for v in vitals:
            data_manager.store_vital_sign(v)

        df = pd.DataFrame(data_manager.get_patient_vitals_history(patient_id, limit=50))
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        fig = go.Figure()
        for sensor in ["ECG", "SpO2", "BP_SYS", "BP_DIA"]:
            sensor_data = df[df["sensor"] == sensor]
            if not sensor_data.empty:
                fig.add_trace(go.Scatter(
                    x=sensor_data["timestamp"],
                    y=pd.to_numeric(sensor_data["value"], errors="coerce"),
                    mode="lines+markers",
                    name=sensor,
                    line=dict(color=sensor_colors.get(sensor, "gray"))  # Default to gray if not mapped
                ))

        fig.update_layout(
            title="📈 Live Multi-Sensor Monitor",
            xaxis_title="Time",
            yaxis_title="Value",
            xaxis=dict(tickformat="%H:%M:%S"),
            legend=dict(orientation="h", y=-0.2)
        )
        graph_placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(refresh_rate)


# --------------------------
# SIDEBAR SUMMARY
# --------------------------
st.sidebar.title("📋 Summary")
summary = twin_manager.get_all_twins_summary()
alerts = alert_manager.get_alert_statistics()
st.sidebar.metric("Total Patients", summary["total_patients"])
st.sidebar.metric("Active Alerts", alerts["active_alerts"])
st.sidebar.metric("High Risk", len(summary["high_risk_patients"]))
