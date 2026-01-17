from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Usamos SQLite para empezar
SQLALCHEMY_DATABASE_URL = "sqlite:///./sistema_financiero.db"

# check_same_thread=False es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyectar la DB en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()