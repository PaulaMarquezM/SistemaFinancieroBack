from fastapi import APIRouter
from app.schemas.interest import CompoundInterestRequest
from app.services.interest import compound_interest

router = APIRouter()

@router.post("/compound")
def calculate_compound(data: CompoundInterestRequest):
    result = compound_interest(
        data.capital,
        data.rate,
        data.periods
    )
    return {"result": round(result, 2)}
