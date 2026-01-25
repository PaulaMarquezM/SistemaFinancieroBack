from fastapi import APIRouter, HTTPException
from app.modules.interes.schema import InteresRequest, InteresResponse
from app.modules.interes.service import (
    convertir_tiempo_a_anios,
    calcular_interes_simple
)

router = APIRouter(prefix="/interes", tags=["Interés"])


@router.post("/calcular", response_model=InteresResponse)
def calcular_interes(data: InteresRequest):

    try:
        tiempo_anios = convertir_tiempo_a_anios(
            data.tiempo,
            data.unidad.lower(),
            data.tipo.lower()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    interes, monto = calcular_interes_simple(
        data.capital,
        data.tasa_anual,
        tiempo_anios
    )

    return InteresResponse(
        interes=round(interes, 2),
        monto=round(monto, 2),
        tiempo_anios=round(tiempo_anios, 6)
    )
