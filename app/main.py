from fastapi import FastAPI
from app.core.cors import setup_cors
from app.core.database import engine, Base

# Importamos los routers (modulares)
from app.api.v1.interest import router as interest_router
from app.api.v1.auth import router as auth_router 

# Creamos las tablas en la DB al iniciar (Solo para desarrollo rápido)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Financiero API", version="1.0.0")

# Configuración Centralizada de CORS
setup_cors(app)

# Inclusión de Rutas (Versioning v1)
# Aquí separamos lógica por dominio: Auth, Intereses, etc.
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(interest_router, prefix="/api/v1/interest", tags=["Interest"])

@app.get("/")
def read_root():
    return {"message": "Sistema Financiero API is running correctly"}