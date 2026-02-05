from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Credit(Base):
    __tablename__ = "credits"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Loan parameters
    principal = Column(Float, nullable=False)
    annual_rate = Column(Float, nullable=False)
    periods = Column(Integer, nullable=False)
    method = Column(String, nullable=False)  # 'frances' or 'aleman'

    # Calculated totals
    total_interest = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    monthly_payment = Column(Float)  # Only fixed for 'frances' method

    # Status and metadata
    status = Column(String, default="active", index=True)  # active, paid, defaulted, cancelled
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="credits")
    payments = relationship("CreditPayment", back_populates="credit", cascade="all, delete-orphan")
