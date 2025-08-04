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
# LIVE MULTI-SENSOR GRAPH + ICU GAUGES
# --------------------------
import time

st.subheader("📡 Live Vitals Monitoring")
auto_refresh = st.checkbox("Enable Auto Mode", value=True)
refresh_rate = st.slider("Refresh Interval (seconds)", 1, 10, 3)

graph_placeholder = st.empty()
desc_placeholder = st.empty()
gauge_placeholder = st.empty()

# Colors
sensor_colors = {
    "ECG": "red",
    "SpO2": "blue",
    "BP_SYS": "green",
    "BP_DIA": "orange"
}

ranges = {
    "ECG": {"safe": (60, 100), "borderline": (50, 110)},
    "SpO2": {"safe": (95, 100), "borderline": (90, 94)},
    "BP_SYS": {"safe": (90, 130), "borderline": (80, 140)},
    "BP_DIA": {"safe": (60, 90), "borderline": (50, 95)}
}

if auto_refresh:
    for _ in range(200):
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
        alert_messages = []
        latest_values = {}

        for sensor in ["ECG", "SpO2", "BP_SYS", "BP_DIA"]:
            sensor_data = df[df["sensor"] == sensor]
            if not sensor_data.empty:
                y_values = pd.to_numeric(sensor_data["value"], errors="coerce")
                latest_values[sensor] = y_values.iloc[-1]

                fig.add_trace(go.Scatter(
                    x=sensor_data["timestamp"],
                    y=y_values,
                    mode="lines+markers",
                    name=sensor,
                    line=dict(color=sensor_colors[sensor])
                ))

                safe_low, safe_high = ranges[sensor]["safe"]
                border_low, border_high = ranges[sensor]["borderline"]

                fig.add_hrect(y0=safe_low, y1=safe_high, fillcolor="green", opacity=0.1, line_width=0)
                fig.add_hrect(y0=border_low, y1=safe_low, fillcolor="yellow", opacity=0.1, line_width=0)
                fig.add_hrect(y0=safe_high, y1=border_high, fillcolor="yellow", opacity=0.1, line_width=0)
                fig.add_hrect(y0=border_high, y1=max(y_values)+10, fillcolor="red", opacity=0.1, line_width=0)
                fig.add_hrect(y0=min(y_values)-10, y1=border_low, fillcolor="red", opacity=0.1, line_width=0)

                latest_value = latest_values[sensor]
                if latest_value < border_low or latest_value > border_high:
                    alert_messages.append(f"🚨 {sensor}: {latest_value} (Critical)")
                elif latest_value < safe_low or latest_value > safe_high:
                    alert_messages.append(f"⚠ {sensor}: {latest_value} (Borderline)")

        fig.update_layout(
            title="📈 ICU Live Multi-Sensor Monitor",
            xaxis_title="Time",
            yaxis_title="Value",
            xaxis=dict(tickformat="%H:%M:%S"),
            legend=dict(orientation="h", y=-0.2)
        )

        graph_placeholder.plotly_chart(fig, use_container_width=True)

        if alert_messages:
            desc_placeholder.error("\n".join(alert_messages))
        else:
            desc_placeholder.success("✅ All vitals in safe range.")

        # --------------------------
        # ICU Digital Gauges
        # --------------------------
        gauge_cols = gauge_placeholder.columns(4)
        for i, sensor in enumerate(["ECG", "SpO2", "BP_SYS", "BP_DIA"]):
            if sensor in latest_values:
                val = latest_values[sensor]
                color = sensor_colors[sensor]
                gauge_cols[i].markdown(
                    f"""
                    <div style='text-align:center; padding:10px; background-color:black; border-radius:10px;'>
                        <h4 style='color:white'>{sensor}</h4>
                        <h2 style='color:{color}'>{val:.1f}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
