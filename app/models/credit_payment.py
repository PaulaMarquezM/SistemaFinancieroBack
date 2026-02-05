from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CreditPayment(Base):
    __tablename__ = "credit_payments"

    id = Column(Integer, primary_key=True, index=True)
    credit_id = Column(Integer, ForeignKey("credits.id"), nullable=False, index=True)
    period_number = Column(Integer, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)

    # Expected values from amortization schedule
    expected_payment = Column(Float, nullable=False)
    expected_principal = Column(Float, nullable=False)
    expected_interest = Column(Float, nullable=False)
    expected_balance = Column(Float, nullable=False)

    # Actual payment tracking
    paid_amount = Column(Float, default=0)
    paid_date = Column(DateTime(timezone=True))
    is_paid = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    credit = relationship("Credit", back_populates="payments")
