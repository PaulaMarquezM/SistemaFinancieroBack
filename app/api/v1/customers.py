from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter()


def _model_dump(payload: CustomerCreate) -> dict:
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()


@router.post("/", response_model=CustomerResponse)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    # Pre-check unique constraints for clearer errors
    if db.query(Customer).filter(Customer.document_number == payload.document_number).first():
        raise HTTPException(status_code=400, detail="Document number already registered")

    if payload.email:
        if db.query(Customer).filter(Customer.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

    customer = Customer(**_model_dump(payload))
    db.add(customer)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Customer already exists")

    return customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(Customer).offset(skip).limit(limit).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Usamos tu función auxiliar para obtener los datos
    update_data = _model_dump(payload)

    # Validar que no estemos duplicando documento/email de OTRA persona
    if db.query(Customer).filter(Customer.document_number == payload.document_number, Customer.id != customer_id).first():
        raise HTTPException(status_code=400, detail="Document number already registered by another customer")
        
    if payload.email:
        if db.query(Customer).filter(Customer.email == payload.email, Customer.id != customer_id).first():
             raise HTTPException(status_code=400, detail="Email already registered by another customer")

    # Actualizar campos
    for key, value in update_data.items():
        setattr(customer, key, value)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed")

    return customer