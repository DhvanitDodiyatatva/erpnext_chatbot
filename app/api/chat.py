from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.realtime_ingest import ingest_incremental_data
from sqlalchemy.orm import Session
from app.models.chat_schema import ChatRequest, ChatResponse
from app.api.deps import get_db
from app.models.schemas import Customer
from app.services.search import search_context
from app.services.llm import generate_answer
from app.services.sql_generator import generate_sql
from app.services.sql_executor import execute_sql
from app.services.answer_formatter import format_answer

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

# @router.post("/chat")
# def chat(req: ChatRequest):
#     ingest_incremental_data()

#     context = search_context(req.question)
#     answer = generate_answer(context, req.question)

#     return {"answer": answer}
@router.post("/chat")
def chat(req: ChatRequest):
    question = req.question

    try:
        #  Step 1: Try SQL
        sql = generate_sql(question)
        data = execute_sql(sql)

        if data:
            answer = format_answer(question, data)
            return {"answer": answer, "sql": sql}

    except Exception:
        pass  # fallback to RAG

    #  Step 2: Fallback to RAG
    context = search_context(question)
    answer = generate_answer(context, question)

    return {"answer": answer}