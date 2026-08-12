"""
Metin parcalama (chunking).

Hukuki metinler icin onerilen yaklasim:
    - RecursiveCharacterTextSplitter, separators=["\\n\\n", "\\n", ". ", " "]
    - chunk_size ~800 karakter (~150-200 token), overlap ~200
    - Klozlarin ortasindan bolunmemesi icin overlap onemli

TODO:
    - [ ] chunk_documents(): ContractDocument listesini al, chunk listesi don
    - [ ] Her chunk'a contract_id + chunk_index metadata'sini ekle (kaynak gosterimi icin sart)
"""
from __future__ import annotations

from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import settings
from rag.ingest import ContractDocument


@dataclass
class Chunk:
    chunk_id: str
    contract_id: str
    text: str
    metadata: dict


def get_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )


def chunk_documents(documents: list[ContractDocument]) -> list[Chunk]:
    """TODO: implement - splitter'i kullanarak dokumanlari chunk'lara ayir."""
    splitter = get_splitter()
    del splitter  # placeholder, implement asagida
    raise NotImplementedError("TODO: dokumanlari chunk'lara ayir, kaynak metadata ekle")
