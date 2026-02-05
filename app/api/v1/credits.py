from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.schemas.credit import CreditCreate, CreditResponse, CreditWithPayments
from app.schemas.credit_payment import CreditPaymentResponse, PaymentRegister
from app.services import credit_service

router = APIRouter()


@router.post("/", response_model=CreditResponse)
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
