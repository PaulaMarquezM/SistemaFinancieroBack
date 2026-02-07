from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class AccountReceivableBase(BaseModel):
    customer_id: Optional[int] = None
    customer_name: str = Field(..., min_length=2)
    amount_due: float = Field(..., gt=0)
    due_date: date
    status: str = Field("pending")
    description: Optional[str] = None


class AccountReceivableCreate(AccountReceivableBase):
    pass


class AccountReceivableResponse(AccountReceivableBase):
    id: int

    class Config:
        from_attributes = True


class AccountReceivableReportRow(BaseModel):
    id: int
    customer_name: str
    amount_due: float
    due_date: date
    status: str


class AccountReceivableMonthlyReport(BaseModel):
    month: str
    total_amount: float
    count: int
    rows: List[AccountReceivableReportRow]
