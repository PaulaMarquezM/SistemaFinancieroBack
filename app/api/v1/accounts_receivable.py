from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.report_config import get_report_header, get_logo_path
from app.schemas.account_receivable import (
    AccountReceivableResponse,
    AccountReceivableMonthlyReport,
)
from app.services import account_receivable_service

router = APIRouter()


@router.get("/pending", response_model=list[AccountReceivableResponse])
def list_pending(db: Session = Depends(get_db)):
    return account_receivable_service.list_pending(db)


@router.get("/monthly-report", response_model=AccountReceivableMonthlyReport)
def monthly_report(
    month: str = Query(..., description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
):
    try:
        return account_receivable_service.get_monthly_report(db, month)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid month. Use YYYY-MM.")


def _build_pdf(report_header: dict, report: dict) -> BytesIO:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="reportlab is not installed") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    elements = []
    logo_path = get_logo_path()
    logo = ""
    if logo_path:
        logo = Image(logo_path, width=0.7 * inch, height=0.7 * inch)

    header_text = (
        f"<b>{report_header['coop_name']}</b><br/>"
        f"{report_header['report_type']}<br/>"
        f"Fecha emision: {report_header['issued_date']}<br/>"
        f"Responsable: {report_header['responsible']}"
    )
    header_table = Table(
        [[logo, Paragraph(header_text, styles["Normal"])]],
        colWidths=[0.9 * inch, 5.5 * inch],
        hAlign="LEFT",
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    table_data = [["ID", "Cliente", "Fecha Venc.", "Monto", "Estado"]]
    for row in report["rows"]:
        table_data.append(
            [
                row["id"],
                row["customer_name"],
                row["due_date"].isoformat(),
                f"{row['amount_due']:.2f}",
                row["status"],
            ]
        )

    table_data.append(["", "", "Total", f"{report['total_amount']:.2f}", ""])

    table = Table(
        table_data,
        colWidths=[0.7 * inch, 2.8 * inch, 1.3 * inch, 1.2 * inch, 1.1 * inch],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A3143")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 1), (-1, -2), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F1F5F9")]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E2E8F0")),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ("ALIGN", (4, 0), (4, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def _build_excel(report_header: dict, report: dict) -> BytesIO:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="openpyxl is not installed") from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Cuentas por Cobrar"

    ws.append([report_header["coop_name"]])
    ws.append([report_header["report_type"]])
    ws.append([f"Fecha emision: {report_header['issued_date']}"])
    ws.append([])

    ws.append(["ID", "Cliente", "Fecha Venc.", "Monto", "Estado"])
    for row in report["rows"]:
        ws.append(
            [
                row["id"],
                row["customer_name"],
                row["due_date"].isoformat(),
                float(row["amount_due"]),
                row["status"],
            ]
        )

    ws.append([])
    ws.append(["", "", "Total", float(report["total_amount"]), ""])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


@router.get("/export/pdf")
def export_pdf(
    month: str = Query(..., description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
):
    report = account_receivable_service.get_monthly_report(db, month)
    header = get_report_header("Reporte de cuentas por cobrar")
    pdf_buffer = _build_pdf(header, report)
    filename = f"accounts_receivable_{month}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/excel")
def export_excel(
    month: str = Query(..., description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
):
    report = account_receivable_service.get_monthly_report(db, month)
    header = get_report_header("Reporte de cuentas por cobrar")
    excel_buffer = _build_excel(header, report)
    filename = f"accounts_receivable_{month}.xlsx"
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
