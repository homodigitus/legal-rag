"""
ChromaDB - tamamen local, diskte persist eden vektor veritabani.
Bulut baglantisi gerektirmez (EPDK/on-prem kisitina uygun).

TODO:
    - [ ] get_vectorstore(): persist edilmis Chroma collection'i don (yoksa olustur)
    - [ ] add_chunks(): Chunk listesini embed edip collection'a ekle
    - [ ] reset_collection(): gelistirme sirasinda temizden baslamak icin
"""
from __future__ import annotations

from functools import lru_cache

import chromadb
from langchain_chroma import Chroma

from rag.config import settings
from rag.embeddings import get_embedding_model


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def get_vectorstore() -> Chroma:
    client = get_chroma_client()
    return Chroma(
        client=client,
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_model(),
        persist_directory=settings.chroma_persist_dir,
    )


def reset_collection() -> None:
    """Gelistirme/deneme sirasinda collection'i sifirlamak icin."""
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection_name)
    except Exception:
        pass


def add_chunks(chunks: list) -> None:
    """TODO: implement - Chunk listesini vectorstore'a yaz."""
    raise NotImplementedError("TODO: chunks -> Documents -> vectorstore.add_documents")
