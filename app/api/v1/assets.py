from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.asset import (
    AssetCreate,
    AssetResponse,
    AssetDepreciationResponse,
    AssetMonthlyReportResponse,
)
from app.services import asset_service
from app.models.asset import Asset

router = APIRouter()


@router.post("/", response_model=AssetResponse)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    asset = Asset(**payload.model_dump())
    return asset_service.create_asset(db, asset)


@router.get("/", response_model=list[AssetResponse])
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
        raise HTTPException(status_code=400, detail="Invalid month. Use YYYY-MM.")
