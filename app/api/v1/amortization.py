# app/api/v1/amortization.py
from fastapi import APIRouter, HTTPException
from app.schemas.amortization import AmortizationRequest, AmortizationResponse
from app.services.amortization import calculate_amortization_schedule

router = APIRouter()

@router.post("/calculate", response_model=AmortizationResponse)
def get_amortization_schedule(data: AmortizationRequest):
    schedule = calculate_amortization_schedule(
        data.principal,
        data.annual_rate,
        data.periods,
        data.method
    )

    if not schedule:
        raise HTTPException(status_code=400, detail="Invalid parameters for calculation")

    return {"schedule": schedule}