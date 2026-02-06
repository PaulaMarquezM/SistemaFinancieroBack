from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import Base, SessionLocal, engine
from app.models.credit import Credit
from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.services.amortization import calculate_amortization_schedule


SEED_TAG = "SEED2026"

START_DATES = [
    "2026-01-01",
    "2026-01-04",
    "2026-01-07",
    "2026-01-10",
    "2026-01-13",
    "2026-01-16",
    "2026-01-19",
    "2026-01-22",
    "2026-01-25",
    "2026-01-28",
    "2026-01-31",
    "2026-02-03",
    "2026-02-05",
    "2026-02-07",
    "2026-02-09",
]


CREDIT_TEMPLATES = [
    {"principal": "8000", "annual_rate": "12", "periods": 12, "method": "frances"},
    {"principal": "12000", "annual_rate": "14", "periods": 18, "method": "aleman"},
    {"principal": "15000", "annual_rate": "16", "periods": 24, "method": "frances"},
    {"principal": "20000", "annual_rate": "18", "periods": 24, "method": "aleman"},
    {"principal": "25000", "annual_rate": "20", "periods": 30, "method": "frances"},
    {"principal": "30000", "annual_rate": "22", "periods": 36, "method": "aleman"},
    {"principal": "18000", "annual_rate": "15", "periods": 12, "method": "frances"},
    {"principal": "22000", "annual_rate": "19", "periods": 18, "method": "aleman"},
    {"principal": "26000", "annual_rate": "21", "periods": 24, "method": "frances"},
    {"principal": "32000", "annual_rate": "23", "periods": 30, "method": "aleman"},
    {"principal": "36000", "annual_rate": "24", "periods": 36, "method": "frances"},
    {"principal": "10000", "annual_rate": "13", "periods": 12, "method": "aleman"},
    {"principal": "14000", "annual_rate": "17", "periods": 18, "method": "frances"},
    {"principal": "28000", "annual_rate": "25", "periods": 30, "method": "aleman"},
    {"principal": "40000", "annual_rate": "26", "periods": 36, "method": "frances"},
]


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def seed_credits() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created = 0
    skipped = 0

    try:
        customers = db.query(Customer).order_by(Customer.id).all()
        if len(customers) < 15:
            raise RuntimeError("Not enough customers to seed credits. Seed customers first.")

        for i in range(15):
            description = f"{SEED_TAG}-{i + 1:02d}"
            exists = db.query(Credit).filter(Credit.description == description).first()
            if exists:
                skipped += 1
                continue

            customer = customers[i]
            template = CREDIT_TEMPLATES[i]
            start_date = _parse_date(START_DATES[i])

            principal = Decimal(template["principal"])
            annual_rate = Decimal(template["annual_rate"])
            periods = int(template["periods"])
            method = template["method"]

            schedule = calculate_amortization_schedule(
                principal=principal,
                annual_rate=annual_rate,
                periods=periods,
                method=method,
            )

            if not schedule:
                raise RuntimeError(f"Failed schedule for credit {description}")

            total_interest = sum(row["interest"] for row in schedule)
            total_amount = sum(row["payment"] for row in schedule)
            monthly_payment = schedule[0]["payment"] if method == "frances" else None

            credit = Credit(
                customer_id=customer.id,
                principal=float(principal),
                annual_rate=float(annual_rate),
                periods=periods,
                method=method,
                total_interest=float(total_interest),
                total_amount=float(total_amount),
                monthly_payment=float(monthly_payment) if monthly_payment else None,
                description=description,
                status="active",
                start_date=start_date,
            )
            db.add(credit)
            db.flush()

            for row in schedule:
                due_date = start_date + timedelta(days=30 * row["period"])
                payment = CreditPayment(
                    credit_id=credit.id,
                    period_number=row["period"],
                    due_date=due_date,
                    expected_payment=float(row["payment"]),
                    expected_principal=float(row["principal"]),
                    expected_interest=float(row["interest"]),
                    expected_balance=float(row["balance"]),
                    is_paid=False,
                )
                db.add(payment)

            created += 1

        db.commit()
    finally:
        db.close()

    print(f"Credits created: {created}, skipped: {skipped}")


if __name__ == "__main__":
    seed_credits()
