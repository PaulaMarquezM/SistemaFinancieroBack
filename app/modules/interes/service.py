def convertir_tiempo_a_anios(tiempo: float, unidad: str, tipo: str) -> float:
    """
    Convierte el tiempo a años.
    - Interés simple: año exacto = 365 días
    - Interés común: año comercial = 360 días
    """

    if unidad == "anios":
        return tiempo

    if unidad == "meses":
        return tiempo / 12

    if unidad == "dias":
        if tipo == "comun":
            return tiempo / 360
        return tiempo / 365

    raise ValueError("Unidad de tiempo no válida")


def calcular_interes_simple(
    capital: float,
    tasa_anual: float,
    tiempo_anios: float
) -> tuple[float, float]:
    """
    Fórmulas:
    I = P * i * t
    M = P + I
    """
    tasa = tasa_anual / 100
    interes = capital * tasa * tiempo_anios
    monto = capital + interes

    return interes, monto
