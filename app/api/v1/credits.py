from datetime import datetime, time, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.credit import CreditCreate, CreditResponse, CreditWithPayments
from app.schemas.credit_payment import CreditPaymentResponse, PaymentRegister
from app.services import credit_service
from app.core.report_config import get_report_header
from app.models.credit import Credit

router = APIRouter()

REPORT_COLUMNS = [
    {"key": "id", "label": "ID", "format": "integer"},
    {"key": "customer_name", "label": "Cliente", "format": "text"},
    {"key": "principal", "label": "Monto", "format": "currency"},
    {"key": "annual_rate", "label": "Tasa (%)", "format": "percent"},
    {"key": "periods", "label": "Plazo (meses)", "format": "integer"},
    {"key": "method_label", "label": "Metodo", "format": "text"},
    {"key": "status", "label": "Estado", "format": "text"},
    {"key": "start_date", "label": "Fecha inicio", "format": "date"},
    {"key": "end_date_estimated", "label": "Fecha fin (est.)", "format": "date"},
    {"key": "total_interest", "label": "Interes total", "format": "currency"},
    {"key": "total_amount", "label": "Monto total", "format": "currency"},
    {"key": "monthly_payment", "label": "Cuota", "format": "currency"},
]


def _parse_date(value: str, field_name: str) -> datetime:
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}. Use YYYY-MM-DD."
        ) from exc
    return dt


def _credit_end_date(start_date: Optional[datetime], periods: int) -> Optional[datetime]:
    if not start_date:
        return None
    return start_date + timedelta(days=30 * periods)


def _method_label(method: str) -> str:
    if method == "frances":
        return "Frances"
    if method == "aleman":
        return "Aleman"
    return method


def _credit_to_report_row(credit: Credit) -> Dict[str, Any]:
    start_date = credit.start_date or credit.created_at
    end_date = _credit_end_date(start_date, credit.periods)
    return {
        "id": credit.id,
        "customer_id": credit.customer_id,
        "customer_name": credit.customer.full_name if credit.customer else None,
        "principal": credit.principal,
        "annual_rate": credit.annual_rate,
        "periods": credit.periods,
        "method": credit.method,
        "method_label": _method_label(credit.method),
        "status": credit.status,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date_estimated": end_date.isoformat() if end_date else None,
        "total_interest": credit.total_interest,
        "total_amount": credit.total_amount,
        "monthly_payment": credit.monthly_payment,
        "description": credit.description,
    }


@router.get("/report/by-date-range")
def report_by_date_range(
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    start_dt = _parse_date(start, "start")
    end_dt = _parse_date(end, "end")

    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End date must be >= start date.")

    start_bound = datetime.combine(start_dt.date(), time.min)
    end_bound = datetime.combine(end_dt.date(), time.max)

    credits = (
        db.query(Credit)
        .filter(Credit.start_date >= start_bound, Credit.start_date <= end_bound)
        .all()
    )

    rows = [_credit_to_report_row(c) for c in credits]

    totals = {
        "count": len(credits),
        "principal": sum(c.principal for c in credits),
        "total_interest": sum(c.total_interest for c in credits),
        "total_amount": sum(c.total_amount for c in credits),
    }

    return {
        "report_header": get_report_header("Reporte de creditos por rango de fechas"),
        "range": {"start": start, "end": end},
        "totals": totals,
        "table": {"columns": REPORT_COLUMNS, "rows": rows},
        "credits": rows,
        "notes": [
            "Fecha fin (est.) calculada como fecha inicio + 30 dias por periodo."
        ],
    }


@router.get("/report/consolidated")
def report_consolidated(db: Session = Depends(get_db)):
    credits = db.query(Credit).all()
    rows = [_credit_to_report_row(c) for c in credits]

    totals = {
        "count": len(credits),
        "principal": sum(c.principal for c in credits),
        "total_interest": sum(c.total_interest for c in credits),
        "total_amount": sum(c.total_amount for c in credits),
    }

    by_month: Dict[str, Dict[str, float]] = {}
    by_status: Dict[str, int] = {}

    for credit in credits:
        start_date = credit.start_date or credit.created_at
        if start_date:
            key = start_date.strftime("%Y-%m")
        else:
            key = "unknown"

        bucket = by_month.setdefault(key, {"count": 0, "total_amount": 0.0})
        bucket["count"] += 1
        bucket["total_amount"] += float(credit.total_amount)

        by_status[credit.status] = by_status.get(credit.status, 0) + 1

    return {
        "report_header": get_report_header("Reporte consolidado de creditos"),
        "totals": totals,
        "by_month": by_month,
        "by_status": by_status,
        "table": {"columns": REPORT_COLUMNS, "rows": rows},
        "credits": rows,
        "notes": [
            "Fecha fin (est.) calculada como fecha inicio + 30 dias por periodo."
        ],
    }


@router.post("/", response_model=CreditWithPayments)
def create_credit(credit_data: CreditCreate, db: Session = Depends(get_db)):
    """Create a new credit with its payment schedule."""
    try:
        credit = credit_service.create_credit(db, credit_data)
        return credit
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CreditResponse])
def list_credits(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List credits with optional filters."""
    return credit_service.get_credits(db, customer_id=customer_id, status=status, skip=skip, limit=limit)


@router.get("/{credit_id}", response_model=CreditWithPayments)
def get_credit(credit_id: int, db: Session = Depends(get_db)):
    """Get a credit with all its payments."""
    credit = credit_service.get_credit(db, credit_id)
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    return credit


@router.delete("/{credit_id}")
def delete_credit(credit_id: int, db: Session = Depends(get_db)):
    """Delete a credit and all its payments."""
    success = credit_service.delete_credit(db, credit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Credit not found")
    return {"message": "Credit deleted successfully"}


@router.get("/{credit_id}/payments", response_model=List[CreditPaymentResponse])
def get_credit_payments(credit_id: int, db: Session = Depends(get_db)):
    """Get all payments (schedule) for a credit."""
    credit = credit_service.get_credit(db, credit_id)
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    return credit_service.get_credit_payments(db, credit_id)


@router.post("/{credit_id}/payments/{payment_id}/pay", response_model=CreditPaymentResponse)
def register_payment(
    credit_id: int,
    payment_id: int,
    payment_data: PaymentRegister,
    db: Session = Depends(get_db)
):
    """Register a payment for a specific period."""
    payment = credit_service.register_payment(db, credit_id, payment_id, payment_data.amount)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
