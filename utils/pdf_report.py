# utils/pdf_report.py

from fpdf import FPDF
from datetime import datetime

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
    pdf.cell(0, 10, "📊 Vitals Data", ln=True)
    pdf.set_font("Arial", "", 12)

    for v in vitals:
        pdf.cell(0, 10,
                 f"{v.sensor_type}: {v.value:.2f} {v.unit} | Quality: {v.quality_score:.2f}",
                 ln=True)

    # Prediction section
    if prediction:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "🔮 AI Prediction", ln=True)
        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 10,
                 f"Type: {prediction.prediction_type} | Value: {prediction.predicted_value:.2f}",
                 ln=True)
        pdf.cell(0, 10,
                 f"Confidence: {prediction.confidence:.2f} | Uncertainty: {prediction.uncertainty:.2f}",
                 ln=True)
        pdf.cell(0, 10,
                 f"Risk Factors: {', '.join(prediction.risk_factors) if prediction.risk_factors else 'None'}",
                 ln=True)

    # Save PDF
    file_path = f"data/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file_path)
    return file_path
