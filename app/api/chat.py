from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.chat_schema import ChatRequest, ChatResponse
from app.api.deps import get_db
from app.models.schemas import Customer
from app.services.search import search_context
from app.services.llm import generate_answer

router = APIRouter()

@router.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [
        {"id": c.id, "name": c.name, "email": c.email}
        for c in customers
    ]


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    context = search_context(request.question)

    answer = generate_answer(
        context=context,
        question=request.question
    )

    return {"answer": answer}