from fastapi import FastAPI

from app.api.doc_chat import router as doc_router
from app.api.erp_chat import router as erp_router

app = FastAPI(title="ERPNext AI Backend")

app.include_router(erp_router)
app.include_router(doc_router)
