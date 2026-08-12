"""
Retrieval katmani: ChromaDB uzerinden semantic search.

TODO:
    - [ ] build_vectorstore(): chunk'lari embed edip Chroma'ya yaz (bkz db/vectorstore.py)
    - [ ] retrieve(): query al, top-k benzer chunk don (kaynak metadata dahil)
    - [ ] (opsiyonel) hybrid search: keyword pre-filter + semantic search
"""
from __future__ import annotations

from db.vectorstore import get_vectorstore
from rag.config import settings


def retrieve(query: str, top_k: int | None = None) -> list[dict]:
    """Query icin en alakali chunk'lari dondurur.

    Donen her eleman: {"text": ..., "score": ..., "source": {contract_id, chunk_index, ...}}

    TODO: implement
    """
    top_k = top_k or settings.retrieval_top_k
    vectorstore = get_vectorstore()
    del vectorstore  # placeholder
    raise NotImplementedError("TODO: similarity_search yap, kaynak metadata ile birlikte don")
