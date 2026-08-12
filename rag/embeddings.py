"""
Embedding modeli - tamamen local calisir (HuggingFace sentence-transformers).
Ilk calistirmada model HuggingFace'ten indirilip local cache'e (~/.cache) kaydedilir,
sonraki calistirmalar internet gerektirmez.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from rag.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )
