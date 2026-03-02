import os
from dotenv import load_dotenv

load_dotenv()

# Base directory of the project (repository root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ERPNEXT_API_KEY = os.getenv("ERPNEXT_API_KEY")

# Paths for document RAG system
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", os.path.join(BASE_DIR, "documents"))
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", os.path.join(BASE_DIR, "chroma_db"))

