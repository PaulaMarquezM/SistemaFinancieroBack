from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.credit import Credit
from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.schemas.credit import CreditCreate
from app.services.amortization import calculate_amortization_schedule


def create_credit(db: Session, credit_data: CreditCreate) -> Credit:
    """Create a credit with its payment schedule."""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == credit_data.customer_id).first()
    if not customer:
        raise ValueError(f"Customer with id {credit_data.customer_id} not found")

    # Calculate amortization schedule
    schedule = calculate_amortization_schedule(
        principal=credit_data.principal,
        annual_rate=credit_data.annual_rate,
        periods=credit_data.periods,
        method=credit_data.method
    )

    if not schedule:
        raise ValueError("Could not calculate amortization schedule")

    # Calculate totals
    total_interest = sum(row["interest"] for row in schedule)
    total_amount = sum(row["payment"] for row in schedule)
    monthly_payment = schedule[0]["payment"] if credit_data.method == 'frances' else None

    # Create credit
    credit = Credit(
        customer_id=credit_data.customer_id,
        principal=float(credit_data.principal),
        annual_rate=float(credit_data.annual_rate),
        periods=credit_data.periods,
        method=credit_data.method,
        total_interest=float(total_interest),
        total_amount=float(total_amount),
        monthly_payment=float(monthly_payment) if monthly_payment else None,
        description=credit_data.description,
        status="active"
    )
    db.add(credit)
    db.flush()  # Get the credit.id

    # Create payment schedule
    start_date = datetime.now()
    for row in schedule:
        due_date = start_date + timedelta(days=30 * row["period"])
        payment = CreditPayment(
            credit_id=credit.id,
            period_number=row["period"],
            due_date=due_date,
            expected_payment=float(row["payment"]),
            expected_principal=float(row["principal"]),
            expected_interest=float(row["interest"]),
            expected_balance=float(row["balance"]),
            is_paid=False
        )
        db.add(payment)

    db.commit()
    db.refresh(credit)
    return credit


def get_credit(db: Session, credit_id: int) -> Optional[Credit]:
    """Get a credit by ID."""
    return db.query(Credit).filter(Credit.id == credit_id).first()


def get_credits(
    db: Session,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Credit]:
    """Get credits with optional filters."""
    query = db.query(Credit)

    if customer_id:
        query = query.filter(Credit.customer_id == customer_id)
    if status:
        query = query.filter(Credit.status == status)

    return query.offset(skip).limit(limit).all()


def delete_credit(db: Session, credit_id: int) -> bool:
    """Delete a credit and its payments (cascade)."""
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    if not credit:
        return False

    db.delete(credit)
    db.commit()
    return True


def get_credit_payments(db: Session, credit_id: int) -> List[CreditPayment]:
    """Get all payments for a credit."""
    return db.query(CreditPayment).filter(
        CreditPayment.credit_id == credit_id
    ).order_by(CreditPayment.period_number).all()


def register_payment(
    db: Session,
    credit_id: int,
    payment_id: int,
    amount: Decimal
) -> Optional[CreditPayment]:
    """Register a payment for a specific period."""
    payment = db.query(CreditPayment).filter(
        CreditPayment.id == payment_id,
        CreditPayment.credit_id == credit_id
    ).first()

    if not payment:
        return None

    payment.paid_amount = float(amount)
    payment.paid_date = datetime.now()
    payment.is_paid = True

    # Check if all payments are made to update credit status
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    all_payments = db.query(CreditPayment).filter(
        CreditPayment.credit_id == credit_id
    ).all()

    if all(p.is_paid for p in all_payments):
        credit.status = "paid"

    db.commit()
    db.refresh(payment)
    return payment
