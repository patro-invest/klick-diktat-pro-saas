import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_din_pdf_report(analysis_data: Dict[str, Any], agency_id: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Klick&Diktat Pro – DIN-Beratungsprotokoll", ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#0b132b"))))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Agentur: {agency_id} | Kunde: {analysis_data.get('kunde_name', 'Unbekannt')}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    table_data = [["Kategorie", "Status", "DIN-Empfehlung"]]
    for check in analysis_data.get("din_checks", []):
        table_data.append([check["kategorie"], check["status"], check["meldung"]])
        
    t = Table(table_data, colWidths=[140, 60, 330])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1c2541")), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    story.append(t)
    doc.build(story)
    return buffer.getvalue()