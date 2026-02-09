from fastapi import FastAPI
from app.core.cors import setup_cors
from app.core.database import engine, Base

# Importamos los routers
from app.api.v1.interest import router as interest_router
from app.api.v1.auth import router as auth_router
from app.api.v1.credits import router as credits_router
from app.api.v1.customers import router as customers_router
from app.api.v1.assets import router as assets_router
from app.api.v1.accounts_receivable import router as accounts_receivable_router
from app.api.v1.interes import router as interes_v1_router
from app.api.v1 import amortization # Importación del módulo completo si es necesario
from app.modules.interes.router import router as interes_router # Router modular antiguo/alternativo

# Creamos las tablas en la DB al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Financiero API", version="1.0.0")

# Configuración Centralizada de CORS
setup_cors(app)

# --- INCLUSIÓN DE RUTAS ---

# Autenticación e Intereses básicos
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(interest_router, prefix="/api/v1/interest", tags=["Interest"])

# Módulos Principales
app.include_router(amortization.router, prefix="/api/v1/amortization", tags=["Amortization"])
app.include_router(credits_router, prefix="/api/v1/credits", tags=["Credits"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])

# CORRECCIÓN AQUÍ: Cambiamos el prefix para que coincida con el Frontend (/api/v1/receivables)
app.include_router(accounts_receivable_router, prefix="/api/v1/receivables", tags=["Accounts Receivable"])

app.include_router(interes_v1_router, prefix="/api/v1/interes", tags=["Interes"])

# Interés Simple y común (Ruta raíz para compatibilidad)
app.include_router(interes_router)

@app.get("/")
def read_root():
    return {"message": "Sistema Financiero API is running correctly"}