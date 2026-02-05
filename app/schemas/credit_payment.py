from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CreditPaymentResponse(BaseModel):
    id: int
    credit_id: int
    period_number: int
    due_date: datetime
    expected_payment: float
    expected_principal: float
    expected_interest: float
    expected_balance: float
    paid_amount: float
    paid_date: Optional[datetime] = None
    is_paid: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentRegister(BaseModel):
    amount: Decimal
