def export_pdf(rows, path="skillforge_report.pdf"):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as err:
        raise ImportError("PDF export needs ReportLab: pip install reportlab") from err

    pdf, top = canvas.Canvas(path, pagesize=A4), A4[1] - 60
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, top, "SkillForge - Skill Growth Report")
    pdf.setFont("Helvetica", 10)
    y = top - 30
    for row in rows:
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = top
        status = "achieved" if row["achieved"] else "in progress"
        pdf.drawString(
            50,
            y,
            f"{row['name']} | {row['category']} | level {row['level']}/{row['target']}"
            f" | {row['hours']} h | {status}",
        )
        y -= 16
    pdf.save()
    return path
