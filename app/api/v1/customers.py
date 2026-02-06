# app/api/v1/customers.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services import customer_service

router = APIRouter()

@router.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente."""
    db_customer = customer_service.get_customer_by_document(db, document_number=customer.document_number)
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer with this document already exists")
    if customer.email:
        db_customer_email = customer_service.get_customer_by_email(db, email=customer.email)
        if db_customer_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    return customer_service.create_customer(db=db, customer=customer)

@router.get("/", response_model=List[CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos los clientes."""
    return customer_service.get_customers(db, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """Ver un cliente específico."""
    db_customer = customer_service.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Eliminar un cliente."""
    success = customer_service.delete_customer(db, customer_id=customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}
