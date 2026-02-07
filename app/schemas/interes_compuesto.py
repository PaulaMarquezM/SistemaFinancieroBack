from pydantic import BaseModel, Field


class InteresCompuestoRequest(BaseModel):
    capital: float = Field(..., gt=0)
    tasa_anual: float = Field(..., gt=0)
    periodos: int = Field(..., gt=0)


class InteresCompuestoResponse(BaseModel):
    interes: float
    monto: float
    periodos: int
    tasa_anual: float
