from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import Base, SessionLocal, engine
from app.models.customer import Customer


CUSTOMERS = [
    {
        "full_name": "Juan Perez",
        "document_type": "CED",
        "document_number": "0102030405",
        "email": "juan.perez@coop.example.com",
        "phone": "0990000001",
        "address": "Quito",
    },
    {
        "full_name": "Maria Gomez",
        "document_type": "CED",
        "document_number": "0102030406",
        "email": "maria.gomez@coop.example.com",
        "phone": "0990000002",
        "address": "Guayaquil",
    },
    {
        "full_name": "Carlos Ruiz",
        "document_type": "CED",
        "document_number": "0102030407",
        "email": "carlos.ruiz@coop.example.com",
        "phone": "0990000003",
        "address": "Cuenca",
    },
    {
        "full_name": "Luisa Torres",
        "document_type": "CED",
        "document_number": "0102030408",
        "email": "luisa.torres@coop.example.com",
        "phone": "0990000004",
        "address": "Loja",
    },
    {
        "full_name": "Pedro Castro",
        "document_type": "CED",
        "document_number": "0102030409",
        "email": "pedro.castro@coop.example.com",
        "phone": "0990000005",
        "address": "Ambato",
    },
    {
        "full_name": "Ana Molina",
        "document_type": "CED",
        "document_number": "0102030410",
        "email": "ana.molina@coop.example.com",
        "phone": "0990000006",
        "address": "Manta",
    },
    {
        "full_name": "Diego Salazar",
        "document_type": "CED",
        "document_number": "0102030411",
        "email": "diego.salazar@coop.example.com",
        "phone": "0990000007",
        "address": "Machala",
    },
    {
        "full_name": "Sofia Vargas",
        "document_type": "CED",
        "document_number": "0102030412",
        "email": "sofia.vargas@coop.example.com",
        "phone": "0990000008",
        "address": "Ibarra",
    },
    {
        "full_name": "Luis Herrera",
        "document_type": "CED",
        "document_number": "0102030413",
        "email": "luis.herrera@coop.example.com",
        "phone": "0990000009",
        "address": "Riobamba",
    },
    {
        "full_name": "Daniela Rios",
        "document_type": "CED",
        "document_number": "0102030414",
        "email": "daniela.rios@coop.example.com",
        "phone": "0990000010",
        "address": "Esmeraldas",
    },
    {
        "full_name": "Miguel Paredes",
        "document_type": "CED",
        "document_number": "0102030415",
        "email": "miguel.paredes@coop.example.com",
        "phone": "0990000011",
        "address": "Portoviejo",
    },
    {
        "full_name": "Valeria Santos",
        "document_type": "CED",
        "document_number": "0102030416",
        "email": "valeria.santos@coop.example.com",
        "phone": "0990000012",
        "address": "Santo Domingo",
    },
    {
        "full_name": "Andres Leon",
        "document_type": "CED",
        "document_number": "0102030417",
        "email": "andres.leon@coop.example.com",
        "phone": "0990000013",
        "address": "Babahoyo",
    },
    {
        "full_name": "Paula Cardenas",
        "document_type": "CED",
        "document_number": "0102030418",
        "email": "paula.cardenas@coop.example.com",
        "phone": "0990000014",
        "address": "Latacunga",
    },
    {
        "full_name": "Jose Morales",
        "document_type": "CED",
        "document_number": "0102030419",
        "email": "jose.morales@coop.example.com",
        "phone": "0990000015",
        "address": "Quevedo",
    },
]


def seed_customers() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created = 0
    skipped = 0

    try:
        for data in CUSTOMERS:
            exists = (
                db.query(Customer)
                .filter(Customer.document_number == data["document_number"])
                .first()
            )
            if exists:
                skipped += 1
                continue

            db.add(Customer(**data))
            created += 1

        db.commit()
    finally:
        db.close()

    print(f"Customers created: {created}, skipped: {skipped}")


if __name__ == "__main__":
    seed_customers()
