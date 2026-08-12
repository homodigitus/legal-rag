"""
Uctan uca RAG pipeline: soru -> retrieval -> local LLM -> kaynakli cevap.

Bu dosya notebooks/ icindeki deneysel calismanin "production" haline
tasindigi yerdir. Streamlit app da bu modulu cagirir.

TODO:
    - [ ] answer_question(): retrieve() + local LLM (Ollama) ile cevap uret
    - [ ] Prompt template: cevabi SADECE verilen context'e dayandir, kaynak goster
    - [ ] Kaynaksiz/emin olunmayan durumlarda "bu bilgiyi bulamadim" desin (halusinasyon onleme)
"""
from __future__ import annotations

from dataclasses import dataclass

from langchain_ollama import ChatOllama

from rag.config import settings
from rag.retriever import retrieve

QA_PROMPT_TEMPLATE = """Sen bir hukuki sozlesme analiz asistanisin. Sadece asagida verilen
BAGLAM icindeki bilgiyi kullanarak soruyu cevapla. Baglamda cevap yoksa
"Bu sozlesmede bu bilgiyi bulamadim." de. Cevabini kisa ve net tut, hangi
sozlesme/bolumden geldigini belirt.

BAGLAM:
{context}

SORU: {question}

CEVAP:"""


@dataclass
class RagAnswer:
    answer: str
    sources: list[dict]


def get_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0,
    )


def answer_question(question: str) -> RagAnswer:
    """TODO: implement
    1) retrieve(question) ile ilgili chunk'lari bul
    2) context'i birlestir
    3) QA_PROMPT_TEMPLATE ile local LLM'e sor
    4) RagAnswer(answer, sources) don
    """
    chunks = retrieve(question)
    del chunks
    raise NotImplementedError("TODO: retrieval sonuclarini prompt'a koy, LLM'i cagir")
