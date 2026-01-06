from pydantic import BaseModel

class CompoundInterestRequest(BaseModel):
    capital: float
    rate: float
    periods: int
