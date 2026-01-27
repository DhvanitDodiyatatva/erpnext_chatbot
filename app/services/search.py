from app.services.embeddings import get_embedding
from app.services.vectordb import collection

def search_context(question: str, top_k: int = 3) -> str:
    query_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    return "\n".join(documents)
