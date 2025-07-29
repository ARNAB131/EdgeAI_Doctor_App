# app.py
import streamlit as st
import pandas as pd
import asyncio
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

# --------------------------
# SIDEBAR - SENSOR SELECTION
# --------------------------
st.sidebar.subheader("🎚️ Select Sensors")
use_ecg = st.sidebar.checkbox("ECG", True)
use_spo2 = st.sidebar.checkbox("SpO2", True)
use_bp = st.sidebar.checkbox("BP", True)

# --------------------------
# SIDEBAR - CSV UPLOAD WITH PREDICTION
# --------------------------
st.sidebar.subheader("📤 Upload Vitals CSV")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    try:
        df_uploaded = pd.read_csv(uploaded)
        st.subheader("📄 Uploaded Data")
        st.dataframe(df_uploaded)

        # Prepare CSV for prediction
        df_for_pred = df_uploaded.copy()

        # Keep only feature columns
        cols_to_keep = [col for col in predictor.required_features if col in df_for_pred.columns]
        df_for_pred = df_for_pred[cols_to_keep]

        # Fill missing required features with defaults
        for col in predictor.required_features:
            if col not in df_for_pred.columns:
                df_for_pred[col] = 0

        # Ensure numeric format
        df_for_pred = df_for_pred.apply(pd.to_numeric, errors="coerce").fillna(0)

        # Predict
        csv_predictions = predictor.predict(df_for_pred)
        df_uploaded["Prediction"] = csv_predictions

        # Show predictions
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

    vitals = []

    # ECG
    if use_ecg:
        ecg = loop.run_until_complete(ecg_sensor.read_data())
        vitals.append(ecg)

    # SpO2
    if use_spo2:
        spo2 = loop.run_until_complete(spo2_sensor.read_data())
        vitals.append(spo2)

    # BP
    if use_bp:
        bp_readings = loop.run_until_complete(bp_sensor.read_data())
        if isinstance(bp_readings, list):  # BP_SYS & BP_DIA
            vitals.extend(bp_readings)
        else:
            vitals.append(bp_readings)

    # Store vitals
    for v in vitals:
        data_manager.store_vital_sign(v)

    all_history = data_manager.get_patient_vitals_history(patient_id, limit=30)

    # Prediction
    prediction = predictor.predict_trend(patient_id, all_history)
    if prediction:
        data_manager.store_prediction(prediction)
    predictions = [prediction] if prediction else []

    # Update twin & alerts
    twin_manager.update_twin(patient_id, vitals, predictions)
    twin = twin_manager.get_twin(patient_id)
    alert = alert_manager.generate_alert(patient_id, twin, predictions)

    st.success("✅ Simulation, Prediction & Alert done.")

    # Display vitals
    st.subheader("📊 Current Vitals")
    for v in vitals:
        st.markdown(f"**{v['sensor_type']}**: `{v['value']}` {v['unit']} | Quality: `{v['quality_score']:.2f}`")

    # Display prediction
    if prediction:
        st.subheader("🔮 Prediction")
        st.markdown(f"**{prediction['prediction_type']}** → `{prediction['predicted_value']:.2f}` (Confidence: `{prediction['confidence']:.2f}`)")

    # Display alerts
    if alert:
        st.subheader("🚨 Alert")
        st.error(f"{alert['title']}\n\n{alert['message']}")

# --------------------------
# LIVE MULTI-SENSOR GRAPH
# --------------------------
import time

st.subheader("📡 Live Vitals Monitoring")
auto_refresh = st.checkbox("Enable Auto Mode", value=True)
refresh_rate = st.slider("Refresh Interval (seconds)", 1, 10, 3)

if auto_refresh:
    graph_placeholder = st.empty()

    for _ in range(200):  # Limit refresh cycles for safety
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        vitals = []

        # Read ECG
        if use_ecg:
            ecg = loop.run_until_complete(ecg_sensor.read_data())
            vitals.append(ecg)

        # Read SpO2
        if use_spo2:
            spo2 = loop.run_until_complete(spo2_sensor.read_data())
            vitals.append(spo2)

        # Read BP
        if use_bp:
            bp_readings = loop.run_until_complete(bp_sensor.read_data())
            vitals.extend(bp_readings if isinstance(bp_readings, list) else [bp_readings])

        # Store vitals
        for v in vitals:
            data_manager.store_vital_sign(v)

        # Get full history for plotting
        all_history = data_manager.get_patient_vitals_history(patient_id, limit=50)
        df = pd.DataFrame(all_history)

        # Ensure timestamps are datetime
        df["timestamp"] = pd.to_datetime(df.get("timestamp", datetime.now()), errors="coerce")

        # Build Plotly figure
        fig = go.Figure()

        for sensor in ["ECG", "SpO2", "BP_SYS", "BP_DIA"]:
            sensor_data = df[df["sensor"] == sensor]
            if not sensor_data.empty:
                fig.add_trace(go.Scatter(
                    x=sensor_data["timestamp"],
                    y=pd.to_numeric(sensor_data["value"], errors="coerce"),
                    mode="lines+markers",
                    name=sensor
                ))

        fig.update_layout(
            title="📈 Live Multi-Sensor Monitor",
            xaxis_title="Time",
            yaxis_title="Value",
            xaxis=dict(
                tickformat="%H:%M:%S",
                tickangle=-45
            ),
            legend=dict(orientation="h", y=-0.2)
        )

        graph_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(refresh_rate)


    # Download reports
    pdf_path = generate_pdf(vitals, prediction)
    with open(pdf_path, "rb") as f_pdf:
        st.download_button("📥 Download PDF Report", f_pdf, file_name=pdf_path.split("/")[-1])

    df_all = pd.DataFrame(vitals)
    st.download_button("📥 Download CSV", df_all.to_csv(index=False), "vitals.csv", "text/csv")

import time

st.subheader("📡 Live Vitals Monitoring")
auto_refresh = st.checkbox("Enable Auto Mode", value=True)
refresh_rate = st.slider("Refresh Interval (seconds)", 1, 10, 3)

if auto_refresh:
    graph_placeholder = st.empty()
    
    for _ in range(200):  # Limit refresh cycles for safety
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        vitals = []
        
        # Read ECG
        if use_ecg:
            ecg = loop.run_until_complete(ecg_sensor.read_data())
            vitals.append(ecg)
        
        # Read SpO2
        if use_spo2:
            spo2 = loop.run_until_complete(spo2_sensor.read_data())
            vitals.append(spo2)
        
        # Read BP
        if use_bp:
            bp_readings = loop.run_until_complete(bp_sensor.read_data())
            vitals.extend(bp_readings if isinstance(bp_readings, list) else [bp_readings])
        
        # Store vitals
        for v in vitals:
            data_manager.store_vital_sign(v)
        
        # Update twin + prediction
        all_history = data_manager.get_patient_vitals_history(patient_id, limit=30)
        prediction = predictor.predict_trend(patient_id, all_history)
        predictions = [prediction] if prediction else []
        twin_manager.update_twin(patient_id, vitals, predictions)
        
        with graph_placeholder.container():
            st.subheader("📈 Real-Time Vitals Chart")
            all_sensors = list({v['sensor_type'] for v in vitals})
            
            for sensor in all_sensors:
                history = data_manager.get_patient_vitals_history(patient_id, sensor, limit=30)
                if history:
                    df = pd.DataFrame(history)
                    df["timestamp"] = pd.to_datetime(df.get("timestamp", datetime.now()), errors="coerce")
                    value_col = "value" if "value" in df.columns else df.select_dtypes(include="number").columns[0]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["timestamp"],
                        y=pd.to_numeric(df[value_col], errors="coerce"),
                        mode="lines+markers",
                        name=sensor
                    ))
                    fig.update_layout(title=f"{sensor} - Live", xaxis_title="Time", yaxis_title="Value")
                    st.plotly_chart(fig, use_container_width=True)
        
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
