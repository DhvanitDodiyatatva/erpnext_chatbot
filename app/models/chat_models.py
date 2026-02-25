from pydantic import BaseModel
from typing import Optional


# 🔹 Request Model
class ChatRequest(BaseModel):
    question: str


# 🔹 Response Model
class ChatResponse(BaseModel):
    type: str
    question: str
    answer: str
    sql: Optional[str] = None
