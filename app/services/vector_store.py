from typing import Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.core.config import CHROMA_DB_DIR


_embedding_function: Optional[SentenceTransformerEmbeddingFunction] = None
_client: Optional[chromadb.PersistentClient] = None
_documents_collection: Optional[Collection] = None


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DOCUMENTS_COLLECTION_NAME = "documents"


def _get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    return _embedding_function


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    return _client


def get_documents_collection() -> Collection:
    """
    Return (and lazily create) the Chroma collection used for document QA.
    """
    global _documents_collection
    if _documents_collection is None:
        client = _get_client()
        _documents_collection = client.get_or_create_collection(
            name=DOCUMENTS_COLLECTION_NAME,
            embedding_function=_get_embedding_function(),
        )
    return _documents_collection

