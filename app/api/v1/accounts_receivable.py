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

# CORRECCIÓN PRINCIPAL: Ruta /report con year y month separados
@router.get("/report", response_model=AccountReceivableMonthlyReport)
def monthly_report(
    year: int = Query(..., description="Year of the report"),
    month: int = Query(..., description="Month of the report (1-12)"),
    db: Session = Depends(get_db),
):
    # Convertimos los enteros al formato "YYYY-MM" que espera tu servicio
    month_str = f"{year}-{month:02d}"
    
    try:
        return account_receivable_service.get_monthly_report(db, month_str)
    except Exception as e:
        print(f"Error: {e}") # Log para depuración
        raise HTTPException(status_code=400, detail="Error generating report. Check date format.")

# --- FUNCIONES AUXILIARES PARA PDF/EXCEL (Sin cambios en lógica interna) ---

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

# --- ENDPOINTS DE EXPORTACIÓN ACTUALIZADOS ---

@router.get("/export/pdf")
def export_pdf(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month"),
    db: Session = Depends(get_db),
):
    month_str = f"{year}-{month:02d}"
    report = account_receivable_service.get_monthly_report(db, month_str)
    header = get_report_header("Reporte de cuentas por cobrar")
    pdf_buffer = _build_pdf(header, report)
    filename = f"accounts_receivable_{month_str}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/excel")
def export_excel(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month"),
    db: Session = Depends(get_db),
):
    month_str = f"{year}-{month:02d}"
    report = account_receivable_service.get_monthly_report(db, month_str)
    header = get_report_header("Reporte de cuentas por cobrar")
    excel_buffer = _build_excel(header, report)
    filename = f"accounts_receivable_{month_str}.xlsx"
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )