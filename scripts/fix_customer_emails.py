from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import SessionLocal
from app.models.customer import Customer


OLD_DOMAIN = "@coop.local"
NEW_DOMAIN = "@coop.example.com"


def fix_emails() -> None:
    db = SessionLocal()
    updated = 0
    try:
        customers = db.query(Customer).filter(Customer.email.isnot(None)).all()
        for customer in customers:
            if customer.email and customer.email.endswith(OLD_DOMAIN):
                customer.email = customer.email.replace(OLD_DOMAIN, NEW_DOMAIN)
                updated += 1
        db.commit()
    finally:
        db.close()

    print(f"Emails updated: {updated}")


if __name__ == "__main__":
    fix_emails()
