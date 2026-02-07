from io import BytesIO
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.core.report_config import get_report_header, get_logo_path
from app.modules.interes.service import convertir_tiempo_a_anios, calcular_interes_simple
from app.schemas.interes_compuesto import InteresCompuestoRequest, InteresCompuestoResponse

router = APIRouter()


def _build_pdf(report_header: dict, title: str, input_rows: list, result_rows: list) -> BytesIO:
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
        f"{title}<br/>"
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

    input_table = Table([["Campo", "Valor"]] + input_rows, colWidths=[2.2 * inch, 3.8 * inch])
    input_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A3143")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(input_table)
    elements.append(Spacer(1, 0.2 * inch))

    result_table = Table([["Resultado", "Valor"]] + result_rows, colWidths=[2.2 * inch, 3.8 * inch])
    result_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#276E90")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(result_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def _build_excel(report_header: dict, title: str, input_rows: list, result_rows: list) -> BytesIO:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="openpyxl is not installed") from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    ws.append([report_header["coop_name"]])
    ws.append([title])
    ws.append([f"Fecha emision: {report_header['issued_date']}"])
    ws.append([])

    ws.append(["Campo", "Valor"])
    for row in input_rows:
        ws.append(row)

    ws.append([])
    ws.append(["Resultado", "Valor"])
    for row in result_rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def _calculate_simple(capital: float, tasa_anual: float, tiempo: float, unidad: str):
    try:
        tiempo_anios = convertir_tiempo_a_anios(tiempo, unidad.lower(), "simple")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    interes, monto = calcular_interes_simple(capital, tasa_anual, tiempo_anios)
    return tiempo_anios, interes, monto


@router.post("/compuesto", response_model=InteresCompuestoResponse)
def calcular_interes_compuesto(payload: InteresCompuestoRequest):
    rate = payload.tasa_anual / 100
    monto = payload.capital * (1 + rate) ** payload.periodos
    interes = monto - payload.capital
    return {
        "interes": round(interes, 2),
        "monto": round(monto, 2),
        "periodos": payload.periodos,
        "tasa_anual": payload.tasa_anual,
    }


@router.get("/simple/export/pdf")
def export_simple_pdf(
    capital: float = Query(..., gt=0),
    tasa_anual: float = Query(..., gt=0),
    tiempo: float = Query(..., gt=0),
    unidad: str = Query(..., description="dias | meses | anios"),
):
    tiempo_anios, interes, monto = _calculate_simple(capital, tasa_anual, tiempo, unidad)
    header = get_report_header("Reporte de interes simple")
    input_rows = [
        ["Capital", f"{capital:.2f}"],
        ["Tasa anual (%)", f"{tasa_anual:.2f}"],
        ["Tiempo", f"{tiempo} {unidad}"],
        ["Tiempo en anios", f"{tiempo_anios:.6f}"],
    ]
    result_rows = [
        ["Interes", f"{interes:.2f}"],
        ["Monto", f"{monto:.2f}"],
    ]
    pdf_buffer = _build_pdf(header, "Interes Simple", input_rows, result_rows)
    filename = "interes_simple.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/simple/export/excel")
def export_simple_excel(
    capital: float = Query(..., gt=0),
    tasa_anual: float = Query(..., gt=0),
    tiempo: float = Query(..., gt=0),
    unidad: str = Query(..., description="dias | meses | anios"),
):
    tiempo_anios, interes, monto = _calculate_simple(capital, tasa_anual, tiempo, unidad)
    header = get_report_header("Reporte de interes simple")
    input_rows = [
        ["Capital", f"{capital:.2f}"],
        ["Tasa anual (%)", f"{tasa_anual:.2f}"],
        ["Tiempo", f"{tiempo} {unidad}"],
        ["Tiempo en anios", f"{tiempo_anios:.6f}"],
    ]
    result_rows = [
        ["Interes", f"{interes:.2f}"],
        ["Monto", f"{monto:.2f}"],
    ]
    excel_buffer = _build_excel(header, "Interes Simple", input_rows, result_rows)
    filename = "interes_simple.xlsx"
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/compuesto/export/pdf")
def export_compuesto_pdf(
    capital: float = Query(..., gt=0),
    tasa_anual: float = Query(..., gt=0),
    periodos: int = Query(..., gt=0),
):
    rate = tasa_anual / 100
    monto = capital * (1 + rate) ** periodos
    interes = monto - capital
    header = get_report_header("Reporte de interes compuesto")
    input_rows = [
        ["Capital", f"{capital:.2f}"],
        ["Tasa anual (%)", f"{tasa_anual:.2f}"],
        ["Periodos", str(periodos)],
    ]
    result_rows = [
        ["Interes", f"{interes:.2f}"],
        ["Monto", f"{monto:.2f}"],
    ]
    pdf_buffer = _build_pdf(header, "Interes Compuesto", input_rows, result_rows)
    filename = "interes_compuesto.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/compuesto/export/excel")
def export_compuesto_excel(
    capital: float = Query(..., gt=0),
    tasa_anual: float = Query(..., gt=0),
    periodos: int = Query(..., gt=0),
):
    rate = tasa_anual / 100
    monto = capital * (1 + rate) ** periodos
    interes = monto - capital
    header = get_report_header("Reporte de interes compuesto")
    input_rows = [
        ["Capital", f"{capital:.2f}"],
        ["Tasa anual (%)", f"{tasa_anual:.2f}"],
        ["Periodos", str(periodos)],
    ]
    result_rows = [
        ["Interes", f"{interes:.2f}"],
        ["Monto", f"{monto:.2f}"],
    ]
    excel_buffer = _build_excel(header, "Interes Compuesto", input_rows, result_rows)
    filename = "interes_compuesto.xlsx"
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
