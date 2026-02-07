from datetime import date
import calendar
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.asset_depreciation import AssetDepreciation


def _add_months(d: date, months: int) -> date:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _build_depreciation_schedule(asset: Asset) -> List[AssetDepreciation]:
    months = asset.useful_life_years * 12
    residual_value = asset.cost * asset.residual_rate
    base_depreciable = asset.cost - residual_value
    monthly_dep = base_depreciable / months

    schedule: List[AssetDepreciation] = []
    accumulated = 0.0

    for period in range(1, months + 1):
        accumulated = monthly_dep * period
        book_value = asset.cost - accumulated

        depreciation_amount = monthly_dep

        # Ajuste de Ãºltimo periodo para no bajar del residual
        if period == months:
            book_value = residual_value
            depreciation_amount = asset.cost - residual_value - (monthly_dep * (months - 1))
            accumulated = asset.cost - book_value

        schedule.append(
            AssetDepreciation(
                asset_id=asset.id,
                period_number=period,
                period_date=_add_months(asset.acquisition_date, period - 1),
                depreciation_amount=round(float(depreciation_amount), 2),
                accumulated_depreciation=round(float(accumulated), 2),
                book_value=round(float(book_value), 2),
            )
        )

    return schedule


def create_asset(db: Session, asset: Asset) -> Asset:
    db.add(asset)
    db.flush()

    schedule = _build_depreciation_schedule(asset)
    db.add_all(schedule)
    db.commit()
    db.refresh(asset)
    return asset


def list_assets(db: Session) -> List[Asset]:
    return db.query(Asset).order_by(Asset.id.asc()).all()


def get_asset(db: Session, asset_id: int) -> Optional[Asset]:
    return db.query(Asset).filter(Asset.id == asset_id).first()


def get_depreciation_schedule(db: Session, asset_id: int) -> List[AssetDepreciation]:
    return (
        db.query(AssetDepreciation)
        .filter(AssetDepreciation.asset_id == asset_id)
        .order_by(AssetDepreciation.period_number.asc())
        .all()
    )


def get_monthly_report(db: Session, month: str):
    # month format: YYYY-MM
    year_str, month_str = month.split("-")
    year = int(year_str)
    month_num = int(month_str)

    start = date(year, month_num, 1)
    end_day = calendar.monthrange(year, month_num)[1]
    end = date(year, month_num, end_day)

    rows = (
        db.query(AssetDepreciation, Asset)
        .join(Asset, Asset.id == AssetDepreciation.asset_id)
        .filter(AssetDepreciation.period_date >= start)
        .filter(AssetDepreciation.period_date <= end)
        .all()
    )

    result_rows = []
    total = 0.0
    for dep, asset in rows:
        total += dep.depreciation_amount
        result_rows.append(
            {
                "asset_id": asset.id,
                "asset_name": asset.name,
                "category": asset.category,
                "depreciation_amount": dep.depreciation_amount,
            }
        )

    return {
        "month": month,
        "total_depreciation": round(total, 2),
        "rows": result_rows,
    }
