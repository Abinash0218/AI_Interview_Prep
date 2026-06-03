import io
import json
from datetime import datetime
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT

from backend.prompts import CATEGORY_LABELS


def format_chat_txt(title: str, category: str, messages: List[dict]) -> str:
    lines = [
        "=" * 60,
        "AI Interview Preparation Assistant",
        "=" * 60,
        f"Chat Title: {title}",
        f"Category: {CATEGORY_LABELS.get(category, category)}",
        f"Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "=" * 60,
        "",
    ]
    for msg in messages:
        role = msg["role"].upper()
        created = msg.get("created_at", "")
        lines.append(f"[{role}] {created}")
        lines.append(msg["content"])
        lines.append("-" * 40)
        lines.append("")
    return "\n".join(lines)


def format_chat_pdf(title: str, category: str, messages: List[dict]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1a73e8"),
        spaceAfter=12,
    )
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=10, textColor=colors.grey)
    role_style = ParagraphStyle("Role", parent=styles["Heading3"], fontSize=11, textColor=colors.HexColor("#333"))
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_LEFT)

    story = []
    story.append(Paragraph("AI Interview Preparation Assistant", title_style))
    story.append(Paragraph(f"<b>Chat:</b> {title}", meta_style))
    story.append(Paragraph(f"<b>Category:</b> {CATEGORY_LABELS.get(category, category)}", meta_style))
    story.append(Paragraph(f"<b>Exported:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", meta_style))
    story.append(Spacer(1, 0.3 * inch))

    for msg in messages:
        role = msg["role"].capitalize()
        story.append(Paragraph(f"{role}", role_style))
        content = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
        story.append(Paragraph(content, body_style))
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def format_share_payload(title: str, category: str, messages: List[dict]) -> dict:
    return {
        "title": title,
        "category": CATEGORY_LABELS.get(category, category),
        "exported_at": datetime.utcnow().isoformat(),
        "message_count": len(messages),
        "messages": messages,
    }
