from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.core.database import Base

class AccountReceivable(Base):
    __tablename__ = "accounts_receivable"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    credit_id = Column(Integer, ForeignKey("credits.id"), nullable=True) # ✅
    customer_name = Column(String, nullable=False)
    amount_due = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="pending") 
    description = Column(String, nullable=True)