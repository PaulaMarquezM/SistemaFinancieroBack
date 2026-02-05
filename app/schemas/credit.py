from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime
from decimal import Decimal

from app.schemas.credit_payment import CreditPaymentResponse


class CreditBase(BaseModel):
    principal: Decimal
    annual_rate: Decimal
    periods: int
    method: Literal['frances', 'aleman']
    description: Optional[str] = None


class CreditCreate(CreditBase):
    customer_id: int


class CreditResponse(BaseModel):
    id: int
    customer_id: int
    principal: float
    annual_rate: float
    periods: int
    method: str
    total_interest: float
    total_amount: float
    monthly_payment: Optional[float] = None
    status: str
    start_date: datetime
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreditWithPayments(CreditResponse):
    payments: List[CreditPaymentResponse] = []
