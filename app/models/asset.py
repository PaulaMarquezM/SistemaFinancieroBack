from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True) # Ej: "Vehículos", "Computo"
    cost = Column(Float, nullable=False)
    residual_rate = Column(Float, nullable=False, default=0.10) # 10% por defecto
    useful_life_years = Column(Integer, nullable=False)
    acquisition_date = Column(Date, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con la tabla de depreciación
    depreciations = relationship(
        "AssetDepreciation",
        back_populates="asset",
        cascade="all, delete-orphan"
    )

class AssetDepreciation(Base):
    __tablename__ = "asset_depreciations"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    
    period_number = Column(Integer, nullable=False) # Mes 1, Mes 2...
    period_date = Column(Date, nullable=False)      # Fecha exacta del mes
    depreciation_amount = Column(Float, nullable=False)
    accumulated_depreciation = Column(Float, nullable=False)
    book_value = Column(Float, nullable=False)

    asset = relationship("Asset", back_populates="depreciations")