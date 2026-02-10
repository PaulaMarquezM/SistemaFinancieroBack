from fastapi import FastAPI
from app.core.cors import setup_cors
from app.core.database import engine, Base

# --- IMPORTACIÓN DE ROUTERS ---
from app.api.v1.interest import router as interest_router
from app.api.v1.auth import router as auth_router
from app.api.v1.credits import router as credits_router
from app.api.v1.customers import router as customers_router
# ✅ Correcto: Coincide con el archivo assets.py que acabamos de hacer
from app.api.v1.assets import router as assets_router 

# ⚠️ CORRECCIÓN: Si seguiste mis pasos, el archivo se llama receivables.py
from app.api.v1.accounts_receivable import router as accounts_receivable_router 

from app.api.v1.interes import router as interes_v1_router
from app.api.v1 import amortization 
from app.modules.interes.router import router as interes_router 

# Creamos las tablas nuevas (Assets, Depreciations) al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Financiero API", version="1.0.0")

# Configuración de CORS
setup_cors(app)

# --- INCLUSIÓN DE RUTAS (Endpoints) ---

# 1. Módulos Core
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"]) # 👈 Aquí entra la lógica de Activos

# 2. Módulos Financieros
app.include_router(credits_router, prefix="/api/v1/credits", tags=["Credits"])
app.include_router(amortization.router, prefix="/api/v1/amortization", tags=["Amortization"])
app.include_router(interest_router, prefix="/api/v1/interest", tags=["Interest"])
app.include_router(interes_v1_router, prefix="/api/v1/interes", tags=["Interes V1"])

# 3. Reportes y Cobros
# El prefix coincide con lo que el Frontend espera (/api/v1/receivables)
app.include_router(accounts_receivable_router, prefix="/api/v1/receivables", tags=["Accounts Receivable"])

# 4. Legacy / Compatibilidad
app.include_router(interes_router)

@app.get("/")
def read_root():
    return {"message": "Sistema Financiero API is running correctly"}