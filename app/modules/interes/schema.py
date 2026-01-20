from pydantic import BaseModel, Field

class InteresRequest(BaseModel):
    capital: float = Field(..., gt=0, description="Capital inicial (P)")
    tasa_anual: float = Field(..., gt=0, description="Tasa anual en porcentaje")
    tiempo: float = Field(..., gt=0, description="Tiempo del préstamo/inversión")
    unidad: str = Field(..., description="dias | meses | anios")
    tipo: str = Field(..., description="simple | comun")


class InteresResponse(BaseModel):
    interes: float
    monto: float
    tiempo_anios: float
