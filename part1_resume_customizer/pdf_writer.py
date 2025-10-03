\
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_LEFT

def build_pdf(path: str, name: str, sections: dict):
    doc = SimpleDocTemplate(path, pagesize=LETTER,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()

    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, spaceAfter=6)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, spaceBefore=6, spaceAfter=4)
    body = ParagraphStyle('Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=12)
    bullet = ParagraphStyle('Bullet', parent=body, leftIndent=12, bulletIndent=0)

    elems = []
    elems.append(Paragraph(name, h1))
    elems.append(Spacer(1, 4))

    for sec_name in ["Summary", "Skills", "Work Experience", "Education"]:
        if sec_name not in sections or not sections[sec_name]:
            continue
        elems.append(Paragraph(sec_name, h2))
        content = sections[sec_name]
        if isinstance(content, list):
            items = [ListItem(Paragraph(x, body)) for x in content]
            elems.append(ListFlowable(items, bulletType='bullet'))
        else:
            elems.append(Paragraph(content, body))
        elems.append(Spacer(1, 6))

    doc.build(elems)
