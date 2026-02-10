from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# Asegúrate de que esta importación sea correcta según tu estructura de carpetas
# A veces es 'app.db.database' o 'app.core.database'
from app.core.database import Base 

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- CORRECCIÓN IMPORTANTE ---
    # Cambiamos full_name por first_name y last_name para coincidir con React
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    # -----------------------------

    # Agregamos un default "CEDULA" por si el frontend no envía el tipo
    document_type = Column(String, nullable=False, default="CEDULA")  
    document_number = Column(String, unique=True, nullable=False, index=True)
    
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con Créditos (Asegúrate de que el modelo Credit exista)
    credits = relationship("Credit", back_populates="customer")