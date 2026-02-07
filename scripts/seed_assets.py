from datetime import date

from app.core.database import SessionLocal, engine, Base
from app.models.asset import Asset
from app.services import asset_service


ASSETS = [
    {
        "name": "Terreno",
        "category": "Terreno",
        "cost": 250000,
        "residual_rate": 0.10,
        "useful_life_years": 20,
        "acquisition_date": date(2026, 1, 1),
    },
    {
        "name": "Equipos de computacion",
        "category": "Equipos de computacion",
        "cost": 80000,
        "residual_rate": 0.10,
        "useful_life_years": 5,
        "acquisition_date": date(2026, 2, 1),
    },
    {
        "name": "Muebles de oficina",
        "category": "Muebles de oficina",
        "cost": 45000,
        "residual_rate": 0.10,
        "useful_life_years": 10,
        "acquisition_date": date(2026, 1, 15),
    },
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for item in ASSETS:
            existing = (
                db.query(Asset)
                .filter(Asset.name == item["name"])
                .filter(Asset.acquisition_date == item["acquisition_date"])
                .first()
            )
            if existing:
                continue

            asset = Asset(**item)
            asset_service.create_asset(db, asset)

        # create_asset already commits per asset
    finally:
        db.close()


if __name__ == "__main__":
    main()
