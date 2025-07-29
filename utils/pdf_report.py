from fpdf import FPDF
from datetime import datetime
import os

def generate_pdf(vitals, prediction):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Patient Vitals Report", ln=True, align='C')
    pdf.set_font("Arial", "", 12)

    # Timestamp
    pdf.ln(5)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Vitals section
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, " Vitals Data", ln=True)
    pdf.set_font("Arial", "", 12)

    for v in vitals:
        sensor_type = v.get("sensor_type", "Unknown")
        value = v.get("value", "N/A")
        unit = v.get("unit", "")
        quality = v.get("quality_score", 0)

        pdf.cell(0, 10,
                 f"{sensor_type}: {value} {unit} | Quality: {quality:.2f}",
                 ln=True)

    # Prediction section
    if prediction:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, " AI Prediction", ln=True)
        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 10,
                 f"Type: {prediction.get('prediction_type', 'N/A')} | Value: {prediction.get('predicted_value', 0):.2f}",
                 ln=True)
        pdf.cell(0, 10,
                 f"Confidence: {prediction.get('confidence', 0):.2f} | Uncertainty: {prediction.get('uncertainty', 0):.2f}",
                 ln=True)
        risk_factors = prediction.get('risk_factors', [])
        pdf.cell(0, 10,
                 f"Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}",
                 ln=True)

    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)
    file_path = f"data/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file_path)

    return file_path
