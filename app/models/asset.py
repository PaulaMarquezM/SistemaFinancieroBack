from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    cost = Column(Float, nullable=False)
    residual_rate = Column(Float, nullable=False, default=0.10)
    useful_life_years = Column(Integer, nullable=False)
    acquisition_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    depreciations = relationship(
        "AssetDepreciation",
        back_populates="asset",
        cascade="all, delete-orphan"
    )
