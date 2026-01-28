from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.realtime_ingest import ingest_incremental_data
from sqlalchemy.orm import Session
from app.models.chat_schema import ChatRequest, ChatResponse
from app.api.deps import get_db
from app.models.schemas import Customer
from app.services.search import search_context
from app.services.llm import generate_answer

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [
        {"id": c.id, "name": c.name, "email": c.email}
        for c in customers
    ]

@router.post("/chat")
def chat(req: ChatRequest):
    ingest_incremental_data()

    context = search_context(req.question)
    answer = generate_answer(context, req.question)

    return {"answer": answer}
