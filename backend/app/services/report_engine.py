import os
import uuid
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import settings
from app.models.cve import CVE


def _ensure_reports_dir() -> str:
    os.makedirs(settings.reports_dir, exist_ok=True)
    return settings.reports_dir


def generate_cve_report_pdf(title: str, cves: list[CVE]) -> str:
    """Render a PDF report listing the given CVEs and return the file path."""
    reports_dir = _ensure_reports_dir()
    filename = f"report_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(reports_dir, filename)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(title, styles["Title"]),
        Paragraph(f"Généré le {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]

    table_data = [["CVE ID", "Sévérité", "CVSS", "Titre", "Publié le"]]
    for cve in cves:
        table_data.append(
            [
                cve.cve_id,
                cve.severity.value if cve.severity else "N/A",
                str(cve.cvss_score) if cve.cvss_score is not None else "N/A",
                Paragraph(cve.title[:90], styles["Normal"]),
                cve.published_at.strftime("%Y-%m-%d") if cve.published_at else "N/A",
            ]
        )

    table = Table(table_data, colWidths=[3 * cm, 2.5 * cm, 1.5 * cm, 7 * cm, 2.5 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(f"Total: {len(cves)} CVE(s)", styles["Normal"]))

    doc.build(elements)
    return file_path
