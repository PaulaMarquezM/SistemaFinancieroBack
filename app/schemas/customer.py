from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- BASE ---
# Estos son los campos comunes. 
# IMPORTANTE: Usamos first_name y last_name para coincidir con el Frontend.
class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # El Frontend manda "document_number". 
    # Ponemos "document_type" con valor por defecto para que no rompa si el front no lo envía.
    document_number: str
    document_type: Optional[str] = "CEDULA" 

# --- CREATE ---
# Lo que recibimos al crear (hereda todo de Base)
class CustomerCreate(CustomerBase):
    pass

# --- UPDATE (NUEVO) ---
# Lo que recibimos al editar. Todo es opcional por si solo quieres cambiar el telefono.
class CustomerUpdate(CustomerBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    document_number: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

# --- RESPONSE ---
# Lo que devolvemos al Frontend (incluye ID y fechas)
class CustomerResponse(CustomerBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Esto es vital para que lea los datos de SQLAlchemy