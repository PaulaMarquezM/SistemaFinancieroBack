# app/services/customer_service.py
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def get_customer_by_document(db: Session, document_number: str):
    return db.query(Customer).filter(Customer.document_number == document_number).first()

def get_customer_by_email(db: Session, email: str):
    return db.query(Customer).filter(Customer.email == email).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: CustomerCreate):
    # Verificar si ya existe por documento o email podría ser buena práctica aquí,
    # pero por simplicidad asumiremos validación en BD (unique constraint) o control en router.
    db_customer = Customer(
        full_name=customer.full_name,
        document_type=customer.document_type,
        document_number=customer.document_number,
        email=customer.email,
        phone=customer.phone,
        address=customer.address
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
        return True
    return False
