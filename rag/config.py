"""Merkezi konfigurasyon. Tum modüller buradan okur, .env'den degerleri cekar."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # LLM
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:e2b-it-qat")

    # Embedding
    hf_api_token: str = os.getenv("HF_API_TOKEN", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embedding_device: str = os.getenv("EMBEDDING_DEVICE", "cpu")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "leoipulsar/harrier-0.6b")
    ollama_embedding_dimensions: int = int(os.getenv("OLLAMA_EMBEDDING_DIMENSIONS", "1024"))

    # Vector DB
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./db/chroma_store")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "cuad_contracts")

    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retrieval
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "4"))

    # Data
    data_raw_dir: str = os.getenv("DATA_RAW_DIR", "./data/raw")
    data_processed_dir: str = os.getenv("DATA_PROCESSED_DIR", "./data/processed")
    cuad_json_path: str = os.getenv("CUAD_JSON_PATH", "./data/raw/CUAD_v1.json")


settings = Settings()
