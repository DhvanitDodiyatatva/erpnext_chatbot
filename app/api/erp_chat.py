from app.services.classify_intent import classify_intent
from app.services.llm import llm_call
from app.services.vector_store import get_documents_collection
from fastapi import APIRouter
import requests
from app.core.config import ERPNEXT_API_KEY
from app.services.sql_generator import generate_sql
from app.services.answer_formatter import format_answer
from app.models.chat_models import ChatRequest, ChatResponse

router = APIRouter()

ERP_EXECUTOR_URL = "http://localhost:8000/api/method/chatbot.api.sql.execute_sql"


@router.post("/erp-chat", response_model=ChatResponse)
def erp_chat(payload: ChatRequest):
    question = payload.question

    # 1️ Classify Intent (ERP_QUERY vs DOCUMENT_QUERY only)
    intent = classify_intent(question)
    print("Detected Intent:", intent)

    # 2️ Handle ERP Query (schema-backed only)
    if intent == "ERP_QUERY":
        sql = generate_sql(question)

        print("--------------------------------------------------------------")
        print("Generated SQL:", sql)
        print("--------------------------------------------------------------")

        sql_lower = sql.lower()
        forbidden = ["insert", "update", "delete", "drop", "alter"]
        if any(word in sql_lower for word in forbidden):
            return ChatResponse(
                type="chat",
                question=question,
                answer="This operation is not allowed.",
            )

        print("--------------------------------------------------------------")
        print("Generated after validate SQL:", sql)
        print("--------------------------------------------------------------")

        response = requests.post(
            ERP_EXECUTOR_URL,
            json={"sql": sql},
            headers={"Authorization": ERPNEXT_API_KEY},
            timeout=30,
        )

        if response.status_code != 200:
            return ChatResponse(
                type="error",
                question=question,
                answer="ERP query execution failed. The requested field may not exist in the schema.",
            )

        try:
            erp_response = response.json()
        except ValueError:
            return ChatResponse(
                type="error",
                question=question,
                answer="Invalid response from ERP system.",
            )

        print("--------------------------------------------------------------")
        print("ERP RAW RESPONSE:", erp_response)
        print("--------------------------------------------------------------")

        #  Safe ERP handling
        if "exception" in erp_response:
            return ChatResponse(
                type="error",
                question=question,
                answer="The requested column does not exist.",
            )

        rows = erp_response.get("message", [])

        answer = format_answer(question, rows)

        return ChatResponse(
            type="erp",
            question=question,
            answer=answer,
            sql=sql,
        )

    # 3️ Handle Document / Vector DB Query (and non-contextual questions)
    if intent == "DOCUMENT_QUERY":
        collection = get_documents_collection()
        results = collection.query(
            query_texts=[question],
            n_results=5,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return ChatResponse(
                type="documents",
                question=question,
                answer=(
                    "I couldn't find any relevant context in the ingested documents. "
                    "I can only answer from the ERP database (consumers, products, quantities, etc.) "
                    "or from uploaded documents (e.g. invoices, policies)."
                ),
            )

        context_blocks = []
        for doc, meta in zip(documents, metadatas):
            source = meta.get("source", "unknown")
            page = meta.get("page")
            location = f"{source}"
            if page is not None:
                location += f" (page {page})"
            context_blocks.append(f"Source: {location}\nContent:\n{doc}")

        context_text = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            "You are a helpful assistant that answers questions based only on the "
            "provided document context. If the context is insufficient or the question "
            "is unrelated to the documents, say you are not sure or that you can only "
            "help with ERP data or document content. Do not guess."
        )

        user_prompt = f"""
You are given context extracted from a set of PDF documents.

Context:
{context_text}

User question:
{question}

Instructions:
- Use only the information from the context above.
- If the answer is not clearly supported by the context, say that you don't know.
- Provide a clear, concise answer. Use bullet points if it improves readability.
"""

        answer = llm_call(system_prompt, user_prompt, temperature=0)

        return ChatResponse(
            type="documents",
            question=question,
            answer=answer,
        )

    # 4️ Fallback (treat as document path)
    return ChatResponse(
        type="documents",
        question=question,
        answer=(
            "I can only answer from the ERP database or from uploaded documents. "
            "Please ask about consumers, products, quantities, or content from your documents."
        ),
    )
