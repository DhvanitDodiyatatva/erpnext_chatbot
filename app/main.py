from fastapi import FastAPI
from app.api.chat import router as chat_router

app = FastAPI(title="PostgreSQL AI Chatbot")

app.include_router(chat_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
