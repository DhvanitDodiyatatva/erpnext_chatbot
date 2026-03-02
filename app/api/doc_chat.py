from fastapi import APIRouter

from app.models.chat_models import ChatRequest, ChatResponse
from app.services.llm import llm_call
from app.services.vector_store import get_documents_collection


router = APIRouter()


@router.post("/doc-chat", response_model=ChatResponse)
def doc_chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question

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
            answer="I couldn't find any relevant context in the ingested documents.",
        )

    # Build a textual context for the LLM
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
        "provided document context. If the context is insufficient, say that "
        "you are not sure instead of guessing."
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

