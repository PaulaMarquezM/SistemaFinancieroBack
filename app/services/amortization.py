# app/services/amortization.py
from typing import List, Dict, Literal
from decimal import *

def calculate_amortization_schedule(
    principal: Decimal,
    annual_rate: Decimal,
    periods: int,
    method: Literal['frances', 'aleman']
) -> List[Dict[str, Decimal]]:

    # Validations
    if principal <= 0 or periods <= 0:
        return []

    # Convert annual rate to monthly rate (assuming monthly payments as per your CSVs)
    # PDF Exercise 1 uses a monthly rate directly, but your CSV uses Annual/12 [cite: 93, 94]
    monthly_rate = (annual_rate / 100) / 12

    balance = principal
    schedule = []

    # Pre-calculate fixed values
    # Sistema Francés: Cuota (Payment) is constant
    # Formula: R = P * [ i(1+i)^n / ((1+i)^n - 1) ] [cite: 53]
    fixed_payment = 0
    if method == 'frances' and monthly_rate > 0:
        fixed_payment = principal * (
            (monthly_rate * (1 + monthly_rate) ** periods) /
            ((1 + monthly_rate) ** periods - 1)
        )

    # Sistema Alemán: Amortización (Principal Payment) is constant
    # Formula: A = P / n
    fixed_principal_amortization = 0
    if method == 'aleman':
        fixed_principal_amortization = principal / periods

    for period in range(1, periods + 1):
        interest_payment = balance * monthly_rate

        if method == 'frances':
            # Francés: Calculate principal part based on fixed total payment
            current_payment = fixed_payment
            principal_payment = current_payment - interest_payment
        else:
            # Alemán: Calculate total payment based on fixed principal part
            principal_payment = fixed_principal_amortization
            current_payment = principal_payment + interest_payment

        balance -= principal_payment

        # Handle last period precision adjustments
        if balance < 0.01:
            balance = 0

        schedule.append({
            "period": period,
            "payment": round(current_payment, 2),     # Cuota Total
            "interest": round(interest_payment, 2),   # Interés
            "principal": round(principal_payment, 2), # Amortización (Capital)
            "balance": round(balance, 2)              # Saldo Final
        })

    return schedule