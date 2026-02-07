from sqlalchemy import Column, Integer, Float, ForeignKey, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AssetDepreciation(Base):
    __tablename__ = "asset_depreciations"
    __table_args__ = (
        UniqueConstraint("asset_id", "period_number", name="uq_asset_period"),
    )

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    period_number = Column(Integer, nullable=False)
    period_date = Column(Date, nullable=False, index=True)

    depreciation_amount = Column(Float, nullable=False)
    accumulated_depreciation = Column(Float, nullable=False)
    book_value = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    asset = relationship("Asset", back_populates="depreciations")
