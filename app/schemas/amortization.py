# app/schemas/amortization.py
from pydantic import BaseModel
from typing import Literal, List
from decimal import *

class AmortizationRequest(BaseModel):
    principal: Decimal
    annual_rate: Decimal
    periods: int
    method: Literal['frances', 'aleman']

class AmortizationRow(BaseModel):
    period: int
    payment: Decimal
    interest: Decimal
    principal: Decimal
    balance: Decimal

class AmortizationResponse(BaseModel):
    schedule: List[AmortizationRow]