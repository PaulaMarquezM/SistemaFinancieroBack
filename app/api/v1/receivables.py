from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List
from datetime import date
from pydantic import BaseModel

from app.core.database import get_db
from app.models.credit_payment import CreditPayment
from app.models.credit import Credit
from app.models.customer import Customer

router = APIRouter()

# --- ESQUEMA DE RESPUESTA (Lo que recibe el Frontend) ---
class ReceivableReportItem(BaseModel):
    fecha_vencimiento: date
    monto_esperado: float
    nombre_cliente: str
    documento_cliente: str
    id_credito: int
    numero_cuota: int
    estado: str

    class Config:
        from_attributes = True

# --- ENDPOINT (La lógica de búsqueda) ---
@router.get("/report", response_model=List[ReceivableReportItem])
def get_monthly_receivables_report(
    year: int = Query(..., description="Año del reporte (ej: 2026)"),
    month: int = Query(..., description="Mes del reporte (1-12)"),
    db: Session = Depends(get_db)
):
    # Buscamos en la base de datos:
    # 1. Pagos que coincidan con el año y mes.
    # 2. Que NO estén pagados (is_paid == False).
    receivables = db.query(CreditPayment)\
        .join(Credit, CreditPayment.credit_id == Credit.id)\
        .join(Customer, Credit.customer_id == Customer.id)\
        .filter(
            extract('year', CreditPayment.due_date) == year,
            extract('month', CreditPayment.due_date) == month,
            CreditPayment.is_paid == False 
        ).all()

    # Formateamos la respuesta para el Frontend
    report_data = []
    for payment in receivables:
        item = ReceivableReportItem(
            fecha_vencimiento=payment.due_date.date(),
            monto_esperado=payment.expected_payment,
            nombre_cliente=payment.credit.customer.full_name,
            documento_cliente=payment.credit.customer.document_number,
            id_credito=payment.credit.id,
            numero_cuota=payment.period_number,
            estado="Pendiente"
        )
        report_data.append(item)

    return report_data