import os

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "rag_service_test")
os.environ.setdefault("POSTGRES_USER", "rag_service_test")
os.environ.setdefault("POSTGRES_PASSWORD", "rag_service_test")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("OLLAMA_API_KEY", "test")
