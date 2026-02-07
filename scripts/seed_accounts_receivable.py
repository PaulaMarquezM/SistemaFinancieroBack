from datetime import date

from app.core.database import SessionLocal, engine, Base
from app.models.account_receivable import AccountReceivable


ROWS = [
    {
        "customer_name": "Cliente Andino",
        "amount_due": 1200.00,
        "due_date": date(2026, 1, 10),
        "status": "pending",
        "description": "Factura enero 2026",
    },
    {
        "customer_name": "Servicios Quito",
        "amount_due": 850.50,
        "due_date": date(2026, 1, 18),
        "status": "pending",
        "description": "Contrato mensual",
    },
    {
        "customer_name": "Comercial Guayas",
        "amount_due": 1500.00,
        "due_date": date(2026, 1, 25),
        "status": "pending",
        "description": "Venta a credito",
    },
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for item in ROWS:
            existing = (
                db.query(AccountReceivable)
                .filter(AccountReceivable.customer_name == item["customer_name"])
                .filter(AccountReceivable.due_date == item["due_date"])
                .first()
            )
            if existing:
                continue

            db.add(AccountReceivable(**item))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
