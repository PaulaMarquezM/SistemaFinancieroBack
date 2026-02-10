import sys
import os
import unicodedata
from faker import Faker
from sqlalchemy.orm import Session

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.customer import Customer

fake = Faker('es_ES')

def clean_string(input_str):
    # Función para quitar tildes y espacios
    nfkd_form = unicodedata.normalize('NFKD', input_str.lower())
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii.replace(" ", "")

def seed_customers():
    db: Session = SessionLocal()
    print("🌱 Sembrando Clientes (Versión Sanitizada)...")

    for _ in range(20):
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Generar email limpio (sin espacios ni tildes)
        clean_first = clean_string(first_name)
        clean_last = clean_string(last_name)
        email = f"{clean_first}.{clean_last}@ejemplo.com"

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": fake.phone_number(),
            "address": fake.address(),
            "document_number": fake.unique.bothify(text='##########')
        }

        existing = db.query(Customer).filter(Customer.email == data["email"]).first()
        if not existing:
            customer = Customer(**data)
            db.add(customer)
    
    try:
        db.commit()
        print("✅ Clientes creados correctamente.")
    except Exception as e:
        print(f"❌ Error al crear clientes: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_customers()