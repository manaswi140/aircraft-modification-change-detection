
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def _create_document(output_path, title):
    """Create a landscape PDF document with shared styles."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        f"{title}Title",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
        spaceAfter=10,
    )

    cell_style = ParagraphStyle(
        f"{title}Cell",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        wordWrap="CJK",
    )

    story = [
        Paragraph(title, title_style),
        Paragraph(
            "Preliminary technical document comparison for human review.",
            styles["Normal"],
        ),
        Spacer(1, 12),
    ]

    return document, styles, title_style, cell_style, story, output_path


def _make_table(table_data, column_widths):
    """Build a consistently formatted report table."""
    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#244062")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [colors.white, colors.HexColor("#F2F5F8")],
        ),
    ]))

    return table


def _paragraph_row(values, cell_style):
    """Convert report values into wrapped PDF table cells."""
    result = []

    for value in values:
        if value is None or value == "":
            text = "—"
        else:
            text = str(value)

        # Escape user/document text before converting line breaks.
        text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

        result.append(Paragraph(text, cell_style))

    return result


def _add_disclaimer(story, styles):
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Disclaimer:</b> This report supports preliminary document "
        "review only. It is not a certification, compliance, or "
        "airworthiness decision. Appropriate human engineering review "
        "is required.",
        styles["Normal"],
    ))


def _format_similarity(value):
    """Format a semantic similarity score for PDF display."""
    if value is None or value == "":
        return "—"

    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def _get_requirement_ids(item):
    """Return the previous, revised, and primary requirement IDs."""
    old_id = item.get("old_id")
    new_id = item.get("new_id")
    requirement_id = (
        item.get("id")
        or new_id
        or old_id
        or "Unknown"
    )

    return (
        old_id or "—",
        new_id or "—",
        requirement_id,
    )


def export_impact_pdf(impact_results, output_path):
    """Export preliminary impact analysis to PDF."""
    (
        document,
        styles,
        _,
        cell_style,
        story,
        output_path,
    ) = _create_document(
        output_path,
        "Modification Impact Analysis Report",
    )

    headers = [
        "Previous ID",
        "Revised ID",
        "Requirement ID",
        "Status",
        "Priority",
        "Numeric Change",
        "Human Review",
        "Semantic Similarity",
        "Potential Impact Areas",
        "Reasons",
    ]

    table_data = [_paragraph_row(headers, cell_style)]

    for item in impact_results:
        old_id, new_id, requirement_id = _get_requirement_ids(item)

        # Support either field naming convention.
        impact_areas = (
            item.get("potential_impact_areas")
            or item.get("impact_areas")
            or []
        )

        impact_reasons = (
            item.get("impact_reasons")
            or item.get("reasons")
            or []
        )

        if isinstance(impact_areas, str):
            impact_areas = [impact_areas]

        if isinstance(impact_reasons, str):
            impact_reasons = [impact_reasons]

        row = [
            old_id,
            new_id,
            requirement_id,
            str(item.get("status", "")).title(),
            item.get("review_priority", ""),
            str(item.get("numeric_change", False)),
            str(item.get("human_review_required", False)),
            _format_similarity(item.get("semantic_similarity")),
            ", ".join(str(area) for area in impact_areas),
            "; ".join(str(reason) for reason in impact_reasons),
        ]

        table_data.append(_paragraph_row(row, cell_style))

    # Total width fits within the available landscape A4 page width.
    column_widths = [
        0.72 * inch,  # Previous ID
        0.72 * inch,  # Revised ID
        0.78 * inch,  # Requirement ID
        0.65 * inch,  # Status
        0.65 * inch,  # Priority
        0.72 * inch,  # Numeric Change
        0.72 * inch,  # Human Review
        0.85 * inch,  # Semantic Similarity
        1.65 * inch,  # Potential Impact Areas
        1.75 * inch,  # Reasons
    ]

    story.append(_make_table(table_data, column_widths))
    _add_disclaimer(story, styles)
    document.build(story)

    return output_path


def export_change_pdf(changes, output_path):
    """Export requirement change results to PDF."""
    (
        document,
        styles,
        _,
        cell_style,
        story,
        output_path,
    ) = _create_document(
        output_path,
        "Modification Change Results Report",
    )

    headers = [
        "Previous ID",
        "Revised ID",
        "Requirement ID",
        "Status",
        "Semantic Similarity",
        "Previous Text",
        "Revised Text",
        "Previous Source / Location",
        "Revised Source / Location",
    ]

    table_data = [_paragraph_row(headers, cell_style)]

    for item in changes:
        old_id, new_id, requirement_id = _get_requirement_ids(item)

        previous_location = " / ".join(
            str(value)
            for value in (
                item.get("old_source"),
                item.get("old_location"),
            )
            if value
        )

        revised_location = " / ".join(
            str(value)
            for value in (
                item.get("new_source"),
                item.get("new_location"),
            )
            if value
        )

        row = [
            old_id,
            new_id,
            requirement_id,
            str(item.get("status", "")).title(),
            _format_similarity(item.get("semantic_similarity")),
            item.get("old_text") or "—",
            item.get("new_text") or "—",
            previous_location or "—",
            revised_location or "—",
        ]

        table_data.append(_paragraph_row(row, cell_style))

    column_widths = [
        0.68 * inch,
        0.68 * inch,
        0.75 * inch,
        0.62 * inch,
        0.82 * inch,
        1.75 * inch,
        1.75 * inch,
        1.45 * inch,
        1.45 * inch,
    ]

    story.append(_make_table(table_data, column_widths))
    _add_disclaimer(story, styles)
    document.build(story)

    return output_path