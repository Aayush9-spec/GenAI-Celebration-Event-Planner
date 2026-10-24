"""
PDF generation service using reportlab Platypus.
Produces a professional event plan PDF with budget table,
timeline, vendor checklist, and theme ideas.
"""

import io
from typing import Any, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Event-type accent colours
ACCENT_COLORS = {
    "wedding": colors.HexColor("#9d174d"),
    "birthday": colors.HexColor("#5b21b6"),
    "community": colors.HexColor("#065f46"),
}
DEFAULT_ACCENT = colors.HexColor("#7c5cd8")


def _get_accent(event_type: str):
    return ACCENT_COLORS.get(event_type, DEFAULT_ACCENT)


def generate_plan_pdf(event: Any, plan: Any) -> bytes:
    """
    Generate a PDF for the given event + plan.
    event: SQLAlchemy Event ORM object
    plan:  SQLAlchemy Plan ORM object
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Event Plan — {event.title}",
        author="GenAI Event Planner",
    )

    styles = getSampleStyleSheet()
    accent = _get_accent(event.event_type)

    # Custom styles
    title_style = ParagraphStyle(
        "EventTitle",
        parent=styles["Title"],
        textColor=accent,
        fontSize=22,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=accent,
        fontSize=14,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = styles["Normal"]
    body_style.fontSize = 10
    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        textColor=colors.HexColor("#57606a"),
        fontSize=9,
    )

    story = []

    # ------------------------------------------------------------------ Header
    story.append(Paragraph(f"🎉 {event.title}", title_style))
    story.append(Paragraph(
        f"{event.event_type.capitalize()} &nbsp;|&nbsp; {event.event_date} "
        f"&nbsp;|&nbsp; {event.guest_count} Guests "
        f"&nbsp;|&nbsp; ₹{event.total_budget:,.0f} INR"
        + (f" &nbsp;|&nbsp; {event.city}" if event.city else ""),
        caption_style,
    ))
    if event.description:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(event.description, caption_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent, spaceAfter=10))

    # ------------------------------------------------------------------ Budget
    budget = plan.budget_breakdown or {}
    items = budget.get("items", [])
    total = budget.get("total", event.total_budget)

    story.append(Paragraph("💰 Budget Breakdown", heading_style))
    if items:
        table_data = [["Category", "Amount (₹)", "Share (%)", "Notes"]]
        for item in items:
            table_data.append([
                item.get("category", "").replace("_", " ").title(),
                f"₹{item.get('amount', 0):,.0f}",
                f"{item.get('percentage', 0):.1f}%",
                item.get("notes", "")[:60],
            ])
        table_data.append(["TOTAL", f"₹{total:,.0f}", "100%", ""])

        t = Table(table_data, colWidths=[5 * cm, 3.5 * cm, 2.5 * cm, 6 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), accent),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.HexColor("#f7f8fa"), colors.white]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e5e7eb")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("Budget breakdown not available.", body_style))

    # ------------------------------------------------------------------ Timeline
    story.append(Paragraph("📅 Event Timeline", heading_style))
    timeline = plan.timeline or {}
    milestones = timeline.get("milestones", [])
    if milestones:
        sorted_ms = sorted(milestones, key=lambda x: x.get("offset", 0))
        tl_data = [["When", "Task", "Priority"]]
        for ms in sorted_ms:
            offset = ms.get("offset", 0)
            unit = ms.get("unit", "week")
            if offset == 0:
                when = "Event Day"
            elif offset < 0:
                when = f"{abs(offset)} {unit}(s) before"
            else:
                when = f"{offset} {unit}(s) after"
            tl_data.append([when, ms.get("task", ""), ms.get("priority", "").capitalize()])

        t = Table(tl_data, colWidths=[3.5 * cm, 11 * cm, 2.5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), accent),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7f8fa"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("Timeline not available.", body_style))

    # ------------------------------------------------------------------ Vendors
    story.append(Paragraph("✅ Vendor Checklist", heading_style))
    vendor_data = plan.vendor_checklist or {}
    categories = vendor_data.get("categories", [])
    if categories:
        for cat in categories:
            story.append(Paragraph(f"<b>{cat['name']}</b>", body_style))
            v_data = [["Task", "Book by (weeks before)", "Tips"]]
            for item in cat.get("items", []):
                v_data.append([
                    item.get("task", ""),
                    str(item.get("deadline_weeks_before", "")) or "—",
                    (item.get("tips", "") or "")[:60],
                ])
            vt = Table(v_data, colWidths=[6 * cm, 3.5 * cm, 7.5 * cm])
            vt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(vt)
            story.append(Spacer(1, 0.3 * cm))
    else:
        story.append(Paragraph("Vendor checklist not available.", body_style))

    # ------------------------------------------------------------------ Theme
    story.append(Paragraph("🎨 Theme & Ideas", heading_style))
    theme = plan.theme_ideas or {}
    rec = theme.get("recommended_theme", "")
    palette = theme.get("color_palette", [])
    ideas = theme.get("ideas", [])
    tips = theme.get("personalization_tips", [])

    if rec:
        story.append(Paragraph(f"<b>Recommended Theme:</b> {rec}", body_style))
    if palette:
        story.append(Paragraph(f"<b>Colour Palette:</b> {', '.join(palette)}", body_style))
    for idea in ideas:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"<b>{idea.get('title', '')}</b> — {idea.get('estimated_cost_impact','').upper()} cost impact", body_style))
        story.append(Paragraph(idea.get("description", ""), caption_style))
    if tips:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("<b>Personalization Tips:</b>", body_style))
        for tip in tips:
            story.append(Paragraph(f"• {tip}", body_style))

    # ------------------------------------------------------------------ Footer
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    story.append(Paragraph(
        "Generated by GenAI Celebration &amp; Event Planner | Powered by Google Gemini",
        caption_style,
    ))

    doc.build(story)
    return buffer.getvalue()
