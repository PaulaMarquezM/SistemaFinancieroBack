from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

# --- BASE ---
class AssetBase(BaseModel):
    name: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    cost: float = Field(..., gt=0)
    residual_rate: float = Field(0.10, ge=0, lt=1)
    useful_life_years: int = Field(..., gt=0)
    acquisition_date: date
    is_active: bool = True

class AssetCreate(AssetBase):
    pass

# --- RESPUESTAS ---
class AssetResponse(AssetBase):
    id: int
    class Config:
        from_attributes = True

# Para la tabla de depreciación detallada
class AssetDepreciationRow(BaseModel):
    period_number: int
    period_date: date
    depreciation_amount: float
    accumulated_depreciation: float
    book_value: float
    class Config:
        from_attributes = True

class AssetDepreciationResponse(BaseModel):
    asset_id: int
    asset_name: str
    schedule: List[AssetDepreciationRow]

# Para el reporte mensual
class AssetMonthlyReportRow(BaseModel):
    asset_id: int
    asset_name: str
    category: str
    depreciation_amount: float

class AssetMonthlyReportResponse(BaseModel):
    month: str
    total_depreciation: float
    rows: List[AssetMonthlyReportRow]