from fastapi import FastAPI
from app.api.v1.interest import router as interest_router
from app.core.cors import setup_cors

app = FastAPI(title="Sistema Financiero API")

setup_cors(app)
app.include_router(interest_router, prefix="/api/v1/interest")
