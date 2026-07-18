import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "4000"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
