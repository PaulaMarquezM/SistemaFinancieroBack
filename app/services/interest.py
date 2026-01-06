def compound_interest(capital: float, rate: float, periods: int) -> float:
    return capital * (1 + rate) ** periods
