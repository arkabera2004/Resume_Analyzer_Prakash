"""Generates a downloadable PDF report for a saved analysis.

Pulls only from what's already stored on the analysis document — no new
computation, no AI calls. This is a formatting layer over data produced by the
other services (ats_scorer, job_matcher, recommendation_service).
"""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY_COLOR = colors.HexColor("#4338CA")
MUTED_COLOR = colors.HexColor("#6B7280")
BORDER_COLOR = colors.HexColor("#E5E7EB")

SCORE_ROWS = [
    ("Keyword Match", "keyword_score"),
    ("Skills Match", "skills_score"),
    ("Resume Structure", "structure_score"),
    ("Experience Relevance", "experience_score"),
    ("Project Relevance", "project_score"),
    ("Formatting", "formatting_score"),
]


def _styles():
    sheet = getSampleStyleSheet()
    sheet.add(ParagraphStyle(name="ReportTitle", fontSize=20, leading=24, textColor=PRIMARY_COLOR, spaceAfter=4))
    sheet.add(ParagraphStyle(name="Subtitle", fontSize=10, textColor=MUTED_COLOR, spaceAfter=16))
    sheet.add(ParagraphStyle(name="Section", fontSize=13, leading=16, spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#111827")))
    sheet.add(ParagraphStyle(name="Body", fontSize=10, leading=14))
    sheet.add(ParagraphStyle(name="Muted", fontSize=9, textColor=MUTED_COLOR))
    return sheet


def _score_table(doc: dict, styles) -> Table:
    rows = [["Category", "Score"]]
    for label, key in SCORE_ROWS:
        value = doc.get(key)
        rows.append([label, str(value) if value is not None else "—"])

    table = Table(rows, colWidths=[3.5 * inch, 1.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ]
        )
    )
    return table


def _bullet_list(items: list[str], styles) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, styles["Body"])) for item in items],
        bulletType="bullet",
        start="•",
        leftIndent=14,
    )


def _skill_paragraph(items: list[str], styles, empty_label: str) -> Paragraph:
    text = ", ".join(items) if items else empty_label
    return Paragraph(text, styles["Body"])


def build_analysis_report(doc: dict) -> bytes:
    """Render a saved analysis document into a PDF, returned as raw bytes."""
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    styles = _styles()
    story = []

    contact = doc.get("parsed_resume", {}).get("contact", {})
    generated_at = datetime.now().strftime("%B %d, %Y")

    # Header
    story.append(Paragraph("Resume Analysis Report", styles["ReportTitle"]))
    subtitle_parts = [doc.get("resume_name", "Resume")]
    if doc.get("job_title"):
        subtitle_parts.append(f"vs. {doc['job_title']}")
    subtitle_parts.append(f"Generated {generated_at}")
    story.append(Paragraph(" · ".join(subtitle_parts), styles["Subtitle"]))

    # Candidate information
    if any(contact.get(field) for field in ("name", "email", "phone", "linkedin", "github")):
        story.append(Paragraph("Candidate Information", styles["Section"]))
        info_lines = []
        if contact.get("name"):
            info_lines.append(f"<b>Name:</b> {contact['name']}")
        if contact.get("email"):
            info_lines.append(f"<b>Email:</b> {contact['email']}")
        if contact.get("phone"):
            info_lines.append(f"<b>Phone:</b> {contact['phone']}")
        if contact.get("linkedin"):
            info_lines.append(f"<b>LinkedIn:</b> {contact['linkedin']}")
        if contact.get("github"):
            info_lines.append(f"<b>GitHub:</b> {contact['github']}")
        story.append(Paragraph("<br/>".join(info_lines), styles["Body"]))

    # ATS score
    if doc.get("ats_score") is not None:
        story.append(Paragraph(f"ATS Score: {doc['ats_score']} / 100", styles["Section"]))
        story.append(_score_table(doc, styles))

    # Job match
    if doc.get("match_score") is not None:
        story.append(Paragraph(f"Job Match: {doc['match_score']}%", styles["Section"]))
        story.append(Paragraph("<b>Matching Skills:</b>", styles["Body"]))
        story.append(_skill_paragraph(doc.get("matching_skills", []), styles, "None detected."))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Missing Skills:</b>", styles["Body"]))
        story.append(_skill_paragraph(doc.get("missing_skills", []), styles, "None."))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Matching Keywords:</b>", styles["Body"]))
        story.append(_skill_paragraph(doc.get("matching_keywords", []), styles, "None detected."))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Missing Keywords:</b>", styles["Body"]))
        story.append(_skill_paragraph(doc.get("missing_keywords", []), styles, "None."))

    # Strengths / weaknesses / priority improvements
    if doc.get("strengths"):
        story.append(Paragraph("Strengths", styles["Section"]))
        story.append(_bullet_list(doc["strengths"], styles))

    if doc.get("weaknesses"):
        story.append(Paragraph("Weaknesses", styles["Section"]))
        story.append(_bullet_list(doc["weaknesses"], styles))

    if doc.get("priority_improvements"):
        story.append(Paragraph("Priority Improvements", styles["Section"]))
        story.append(_bullet_list(doc["priority_improvements"], styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Generated by ResumeIQ — AI Resume Analyzer & Job Match Platform", styles["Muted"]))

    pdf.build(story)
    return buffer.getvalue()
