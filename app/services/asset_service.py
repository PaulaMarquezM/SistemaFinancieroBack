from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from typing import List, Optional
from dateutil.relativedelta import relativedelta  # Recuerda: pip install python-dateutil

# IMPORTANTE: Importamos ambos modelos desde 'asset'
from app.models.asset import Asset, AssetDepreciation 
from app.schemas.asset import AssetMonthlyReportResponse # Para tipado si lo deseas

def create_asset(db: Session, asset: Asset) -> Asset:
    # 1. Guardar el activo para generar su ID
    db.add(asset)
    db.flush()  # Genera el ID sin hacer commit todavía

    # 2. Calcular la tabla usando el ID generado
    schedule = _build_depreciation_schedule(asset)
    
    # 3. Guardar la tabla
    db.add_all(schedule)
    db.commit()
    db.refresh(asset)
    return asset

def _build_depreciation_schedule(asset: Asset) -> List[AssetDepreciation]:
    # Convertimos años a meses
    total_months = asset.useful_life_years * 12
    
    # Cálculos base
    residual_value = asset.cost * asset.residual_rate
    depreciable_amount = asset.cost - residual_value
    monthly_dep = depreciable_amount / total_months

    schedule: List[AssetDepreciation] = []
    
    current_book_value = asset.cost
    accumulated = 0.0
    start_date = asset.acquisition_date

    for i in range(1, total_months + 1):
        # Fecha de cobro: 1 mes después de la compra, 2 meses después, etc.
        period_date = start_date + relativedelta(months=+i)
        
        # Calcular acumulados
        accumulated += monthly_dep
        current_book_value -= monthly_dep
        
        # Valores de este periodo
        this_month_dep = monthly_dep

        # Ajuste en el último mes para cuadrar centavos
        if i == total_months:
            # La diferencia que falte para llegar exacto al valor residual
            remaining = current_book_value - residual_value
            if abs(remaining) > 0.00001:
                this_month_dep += remaining
                accumulated = asset.cost - residual_value
                current_book_value = residual_value

        schedule.append(
            AssetDepreciation(
                asset_id=asset.id,
                period_number=i,
                period_date=period_date,
                depreciation_amount=round(this_month_dep, 2),
                accumulated_depreciation=round(accumulated, 2),
                book_value=round(current_book_value, 2),
            )
        )

    return schedule

def list_assets(db: Session) -> List[Asset]:
    return db.query(Asset).filter(Asset.is_active == True).order_by(Asset.id.asc()).all()

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
    """
    Genera el reporte sumando las depreciaciones de un mes específico.
    Month format: 'YYYY-MM'
    """
    try:
        year_str, month_str = month.split("-")
        year = int(year_str)
        month_num = int(month_str)
    except ValueError:
        raise Exception("Formato de fecha inválido. Use YYYY-MM")

    # Usamos extract de SQLAlchemy para filtrar por año y mes directo en BD
    # (Es más eficiente que traer todo y filtrar en Python)
    rows = (
        db.query(AssetDepreciation, Asset)
        .join(Asset, Asset.id == AssetDepreciation.asset_id)
        .filter(extract('year', AssetDepreciation.period_date) == year)
        .filter(extract('month', AssetDepreciation.period_date) == month_num)
        .all()
    )

    result_rows = []
    total = 0.0
    
    for dep, asset in rows:
        total += dep.depreciation_amount
        result_rows.append({
            "asset_id": asset.id,
            "asset_name": asset.name,
            "category": asset.category,
            "depreciation_amount": round(dep.depreciation_amount, 2),
        })

    return {
        "month": month,
        "total_depreciation": round(total, 2),
        "rows": result_rows,
    }

# ... (al final del archivo asset_service.py)

def delete_asset(db: Session, asset_id: int):
    """Elimina un activo y su tabla de depreciación (por cascada)"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset:
        db.delete(asset)
        db.commit()
        return True
    return False