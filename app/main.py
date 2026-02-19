from fastapi import FastAPI
from app.api.erp_chat import router as erp_router

app = FastAPI(title="ERPNext AI Backend")

app.include_router(erp_router)
