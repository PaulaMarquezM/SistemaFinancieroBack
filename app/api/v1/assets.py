from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.asset import (
    AssetCreate,
    AssetResponse,
    AssetDepreciationResponse,
    AssetMonthlyReportResponse,
)
# Asegúrate de importar tu servicio
from app.services import asset_service
from app.models.asset import Asset

router = APIRouter()

@router.post("/", response_model=AssetResponse)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    # Convertimos el schema Pydantic al modelo SQLAlchemy
    asset = Asset(**payload.dict()) 
    return asset_service.create_asset(db, asset)

@router.get("/", response_model=List[AssetResponse])
def list_assets(db: Session = Depends(get_db)):
    return asset_service.list_assets(db)

@router.get("/{asset_id}/depreciation", response_model=AssetDepreciationResponse)
def get_depreciation(asset_id: int, db: Session = Depends(get_db)):
    asset = asset_service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    schedule = asset_service.get_depreciation_schedule(db, asset_id)
    return {
        "asset_id": asset.id,
        "asset_name": asset.name,
        "schedule": schedule,
    }

@router.get("/monthly-report", response_model=AssetMonthlyReportResponse)
def get_monthly_report(
    month: str = Query(..., description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
):
    try:
        return asset_service.get_monthly_report(db, month)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM.")
    
# ... (asegúrate de tener este import arriba)
from fastapi import status 

# ... (y agrega esto al final del archivo)

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    deleted = asset_service.delete_asset(db, asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return None