# pdf_builder.py

import io
import matplotlib.pyplot as plt
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak
)


# ── Colour palette (matches plots.py) ────────────────────────────────────────
GREEN  = colors.HexColor("#2ecc71")
BLUE   = colors.HexColor("#3498db")
DARK   = colors.HexColor("#2c3e50")
LIGHT  = colors.HexColor("#ecf0f1")
WARN   = colors.HexColor("#f39c12")


# ── Custom styles ─────────────────────────────────────────────────────────────
def _build_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=base["Title"],
        fontSize=20,
        textColor=DARK,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=base["Normal"],
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontSize=14,
        textColor=DARK,
        spaceBefore=14,
        spaceAfter=4,
        borderPad=2,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontSize=11,
        textColor=BLUE,
        spaceBefore=10,
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.grey,
    )
    warn_style = ParagraphStyle(
        "Warning",
        parent=base["Normal"],
        fontSize=9,
        textColor=WARN,
        leftIndent=8,
        spaceAfter=4,
    )
    interp_style = ParagraphStyle(
        "Interpretation",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        leftIndent=12,
        textColor=colors.HexColor("#1a6b3c"),
        spaceAfter=6,
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "h1": h1_style,
        "h2": h2_style,
        "body": body_style,
        "label": label_style,
        "warning": warn_style,
        "interp": interp_style,
    }


# ── Helper: matplotlib figure → reportlab Image ───────────────────────────────
def _fig_to_image(fig, width=6 * inch):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    aspect = fig.get_figheight() / fig.get_figwidth()
    return Image(buf, width=width, height=width * aspect)


# ── Helper: key-value result table ────────────────────────────────────────────
def _result_table(rows, styles_dict):
    """
    rows: list of (label, value) tuples
    """
    data = [[Paragraph(f"<b>{k}</b>", styles_dict["label"]),
             Paragraph(str(v), styles_dict["body"])]
            for k, v in rows]

    t = Table(data, colWidths=[2.2 * inch, 4.3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


# ── Main builder ─────────────────────────────────────────────────────────────
def build_report(
    meta: dict,
    recommended_test: str,
    test_results: dict = None,
    teaching_content: dict = None,
    diagnostics: dict = None,
    figures: list = None,
    student_name: str = "",
) -> bytes:
    """
    Builds a PDF analysis report and returns it as bytes.

    Args:
        meta (dict): study configuration (design, y_type, x_type, etc.)
        recommended_test (str): name of the recommended statistical test
        test_results (dict, optional): results from running the test
        teaching_content (dict, optional): from recommendations.get_teaching_content()
        diagnostics (dict, optional): from diagnostics.run_all_diagnostics()
        figures (list, optional): list of matplotlib Figure objects to embed
        student_name (str): optional student/analyst name for the report header

    Returns:
        bytes: PDF file content
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
    )
    S = _build_styles()
    story = []

    # ── Title block ───────────────────────────────────────────────────────────
    story.append(Paragraph("📊 Public Health Biostatistics Lab", S["title"]))
    subtitle_parts = [f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}"]
    if student_name:
        subtitle_parts.insert(0, f"Analyst: {student_name}")
    story.append(Paragraph("  |  ".join(subtitle_parts), S["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GREEN, spaceAfter=10))

    # ── 1. Study Configuration ────────────────────────────────────────────────
    story.append(Paragraph("1. Study Configuration", S["h1"]))
    config_rows = [
        ("Study Design", meta.get("design", "—").capitalize()),
        ("Outcome Type", meta.get("y_type", "—").capitalize()),
        ("Exposure Type", meta.get("x_type", "—").capitalize()),
    ]
    if meta.get("x_type") == "categorical":
        config_rows.append(("Number of Groups", str(meta.get("groups_k", "—"))))
    if "normal" in meta:
        config_rows.append(("Normality Assumed", "Yes" if meta["normal"] else "No"))
    story.append(_result_table(config_rows, S))
    story.append(Spacer(1, 10))

    # ── 2. Recommended Test ───────────────────────────────────────────────────
    story.append(Paragraph("2. Recommended Statistical Test", S["h1"]))
    story.append(Paragraph(f"<b>{recommended_test}</b>", S["interp"]))

    if teaching_content:
        story.append(Paragraph("What it does:", S["h2"]))
        story.append(Paragraph(teaching_content.get("description", ""), S["body"]))

        story.append(Paragraph("When to use:", S["h2"]))
        story.append(Paragraph(teaching_content.get("when_to_use", ""), S["body"]))

        assumptions = teaching_content.get("assumptions", [])
        if assumptions:
            story.append(Paragraph("Assumptions to check:", S["h2"]))
            for a in assumptions:
                story.append(Paragraph(f"✓  {a}", S["body"]))

        story.append(Paragraph("Effect size measure:", S["h2"]))
        story.append(Paragraph(teaching_content.get("effect_size", ""), S["body"]))

        story.append(Paragraph("Common mistake:", S["h2"]))
        story.append(Paragraph(f"⚠  {teaching_content.get('common_mistake', '')}", S["warning"]))

        story.append(Paragraph("Epidemiology example:", S["h2"]))
        story.append(Paragraph(teaching_content.get("epi_example", ""), S["body"]))

    story.append(Spacer(1, 8))

    # ── 3. Diagnostic Results ─────────────────────────────────────────────────
    if diagnostics:
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT, spaceAfter=6))
        story.append(Paragraph("3. Assumption Diagnostics", S["h1"]))

        norm_results = diagnostics.get("normality", [])
        for nr in norm_results:
            label = nr.get("label") or "Group"
            story.append(Paragraph(f"Normality — {label}", S["h2"]))
            rows = [
                ("Test used", nr.get("test_used", "—")),
                ("Statistic", str(nr.get("statistic", "—"))),
                ("p-value", str(nr.get("p_value", "—"))),
                ("Normally distributed", "Yes" if nr.get("is_normal") else "No"),
                ("Interpretation", nr.get("interpretation", "")),
            ]
            story.append(_result_table(rows, S))
            story.append(Spacer(1, 6))

        var_result = diagnostics.get("equal_variance", {})
        if var_result:
            story.append(Paragraph("Equal Variance (Levene's Test)", S["h2"]))
            rows = [
                ("Statistic", str(var_result.get("statistic", "—"))),
                ("p-value", str(var_result.get("p_value", "—"))),
                ("Equal variance", "Yes" if var_result.get("equal_variance") else "No"),
                ("Interpretation", var_result.get("interpretation", "")),
            ]
            story.append(_result_table(rows, S))
            story.append(Spacer(1, 6))

        story.append(Paragraph(
            f"Overall recommendation: {diagnostics.get('recommendation', '')}",
            S["interp"]
        ))

    # ── 4. Test Results ───────────────────────────────────────────────────────
    if test_results:
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT, spaceAfter=6))
        story.append(Paragraph("4. Statistical Test Results", S["h1"]))

        rows = [(k.replace("_", " ").capitalize(), str(v))
                for k, v in test_results.items()
                if k != "interpretation" and not hasattr(v, "to_dict")]
        if rows:
            story.append(_result_table(rows, S))
            story.append(Spacer(1, 6))

        interp = test_results.get("interpretation")
        if interp:
            story.append(Paragraph(f"Interpretation: {interp}", S["interp"]))

    # ── 5. Figures ────────────────────────────────────────────────────────────
    if figures:
        story.append(PageBreak())
        story.append(Paragraph("5. Figures", S["h1"]))
        for i, fig in enumerate(figures):
            try:
                img = _fig_to_image(fig)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception as e:
                story.append(Paragraph(f"[Figure {i+1} could not be rendered: {e}]", S["warning"]))

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT, spaceAfter=4))
    story.append(Paragraph(
        "Generated by Public Health Biostatistics Lab · For educational use only.",
        S["label"]
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


def save_report(pdf_bytes: bytes, filepath: str):
    """Saves PDF bytes to a file."""
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
