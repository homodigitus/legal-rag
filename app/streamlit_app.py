"""
app/streamlit_app.py

Chat tabanli arayuz: st.chat_message + st.chat_input(accept_file=...).
Kullanici ayni input kutusundan hem dosya yukleyebilir hem soru sorabilir,
hepsi tek bir konusma akisinda devam eder.

Agent tarafinda:
    - Agno Knowledge + ChromaDb (hybrid search), OllamaEmbedder (local, dimensions=1024)
    - search_knowledge=True -> retrieval, agent'in kendi karar verdigi bir tool
    - SqliteDb + session_id + add_history_to_context=True -> chat history
"""
from __future__ import annotations

import io
import sys
import uuid
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.config import settings  # noqa: E402

st.set_page_config(page_title="Eksim - Hukuki Metin Analizi", page_icon="⚖️", layout="wide")
st.title("⚖️ Yerel LLM ile Hukuki Metin Analizi")
st.caption(
    f"Model: `{settings.ollama_model}` (local) · "
    f"Embedding: `{settings.ollama_embedding_model}` (local, {settings.ollama_embedding_dimensions}d) · "
    "Vektor DB: ChromaDB"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_documents" not in st.session_state:
    # Bu oturumda yuklenen dosyalarin metni: {dosya_adi: metin}
    # Session'da yuklenen dokumana soru sorulurken retrieval'e degil,
    # dogrudan bu metne guveniyoruz (kucuk local modelde tool-calling/
    # search tetiklemesi tutarsiz olabiliyor).
    st.session_state.session_documents = {}

SESSION_ID = st.session_state.session_id
MAX_CONTEXT_CHARS = 12000  # prompt'a eklenecek session-dokuman metninin ust siniri


@st.cache_resource(show_spinner=False)
def _get_knowledge():
    from agno.knowledge.embedder.ollama import OllamaEmbedder
    from agno.knowledge.knowledge import Knowledge
    from agno.vectordb.chroma import ChromaDb
    from agno.vectordb.search import SearchType

    embedder = OllamaEmbedder(
        id=settings.ollama_embedding_model,
        dimensions=settings.ollama_embedding_dimensions,
    )
    return Knowledge(
        name="Basic CUAD Knowledge Base",
        description="CUAD Knowledge Implementation with ChromaDB",
        vector_db=ChromaDb(
            collection=settings.chroma_collection_name,
            path=settings.chroma_persist_dir,
            embedder=embedder,
            search_type=SearchType.hybrid,
            persistent_client=True,
        ),
    )


@st.cache_resource(show_spinner=False)
def _get_agent(session_id: str):
    from agno.agent import Agent
    from agno.db.sqlite import SqliteDb
    from agno.models.ollama import Ollama

    db = SqliteDb(db_file="db/agent_history.db")

    return Agent(
        model=Ollama(id=settings.ollama_model),
        db=db,
        session_id=session_id,
        knowledge=_get_knowledge(),
        search_knowledge=True,
        add_history_to_context=True,
        instructions=[
            "Sen Eksim Holding icin calisan bir hukuki sozlesme analiz asistanisin.",
            "SADECE knowledge base'den donen baglama dayanarak cevap ver, tahmin yurutme.",
            "Cevabinda hangi sozlesme/dokumandan bilgi aldigini belirt.",
            "Baglamda cevap yoksa bunu acikca soyle, uydurma.",
            "Onceki mesajlari (chat history) dikkate alarak baglami koru.",
        ],
        markdown=True,
    )


def _ingest_file(uploaded_file) -> tuple[int, str]:
    """Yuklenen dosyayi chunk'layip knowledge base'e ekler.

    Donus: (eklenen chunk sayisi, dosyanin tam duz metni).
    Tam metin, ayni session icinde bu dosyaya dogrudan soru sormak icin
    st.session_state.session_documents'a da yazilir (bkz. caller).
    """
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    raw_bytes = uploaded_file.read()
    if uploaded_file.name.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = raw_bytes.decode("utf-8", errors="ignore")

    doc_name_base = f"{Path(uploaded_file.name).stem}_{SESSION_ID}"
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    docs = splitter.split_documents(
        [Document(page_content=text, metadata={"title": uploaded_file.name, "session_id": SESSION_ID})]
    )

    knowledge = _get_knowledge()
    for i, doc in enumerate(docs):
        knowledge.insert(
            name=f"{doc_name_base}_{i}",
            text_content=doc.page_content,
            metadata=doc.metadata,
        )
    return len(docs), text


# --- Gecmis mesajlari goster (UI render icin; agent'in kendi history'si ayri, db'de) ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input: hem dosya hem soru ayni kutudan ---
prompt = st.chat_input(
    "Sözleşme yükle (.txt/.pdf) ve/veya soru sor...",
    accept_file="multiple",
    file_type=["txt", "pdf"],
)

if prompt:
    # 1) Dosya varsa once onlari isle
    if prompt.files:
        for f in prompt.files:
            st.session_state.messages.append({"role": "user", "content": f"📎 {f.name} yüklendi"})
            with st.chat_message("user"):
                st.markdown(f"📎 **{f.name}** yükleniyor...")
            with st.spinner(f"{f.name} işleniyor..."):
                n_chunks, full_text = _ingest_file(f)
            st.session_state.session_documents[f.name] = full_text
            note = f"✅ **{f.name}** eklendi ({n_chunks} chunk, oturum: `{SESSION_ID}`)"
            st.session_state.messages.append({"role": "assistant", "content": note})
            with st.chat_message("assistant"):
                st.markdown(note)

    # 2) Metin/soru varsa agent'a sor
    if prompt.text and prompt.text.strip():
        st.session_state.messages.append({"role": "user", "content": prompt.text})
        with st.chat_message("user"):
            st.markdown(prompt.text)

        with st.chat_message("assistant"):
            with st.spinner("Agent düşünüyor / knowledge base'i sorguluyor..."):
                agent = _get_agent(SESSION_ID)

                if st.session_state.session_documents:
                    # Kurgu: bu oturumda yuklenmis dosya(lar) varsa, retrieval'e
                    # guvenmek yerine metni DOGRUDAN context olarak veriyoruz.
                    # (Kucuk local modelde search-tool tetiklemesi tutarsiz
                    # olabildigi icin bu yol daha guvenilir.)
                    combined_docs = "\n\n---\n\n".join(
                        f"[{name}]\n{text}"
                        for name, text in st.session_state.session_documents.items()
                    )[:MAX_CONTEXT_CHARS]

                    full_input = (
                        "Asagida bu oturumda kullanicinin yukledigi belge(ler) var. "
                        "SADECE bu belgelere dayanarak soruyu cevapla, knowledge "
                        "base'e veya baska bir kaynaga bakma.\n\n"
                        f"BELGE(LER):\n{combined_docs}\n\n"
                        f"SORU: {prompt.text}"
                    )
                    response = agent.run(full_input, session_id=SESSION_ID)
                else:
                    # Session'da yuklenmis dosya yok -> knowledge base'e bak
                    # (batch yuklenmis CUAD verisi, search_knowledge=True ile)
                    response = agent.run(prompt.text, session_id=SESSION_ID)

                st.markdown(response.content)

        st.session_state.messages.append({"role": "assistant", "content": response.content})

# --- Yan panel: oturum bilgisi + gecmisi temizleme ---
with st.sidebar:
    st.caption(f"Oturum kimliği: `{SESSION_ID}`")

    if st.session_state.session_documents:
        st.caption(f"📎 Bu oturumda yüklenen belgeler ({len(st.session_state.session_documents)}):")
        for name in st.session_state.session_documents:
            st.caption(f"  • {name}")
        st.caption(
            "Sorular bu belgelere göre cevaplanıyor (knowledge base'e değil). "
            "Batch yüklenen CUAD verisine sormak için önce belgeleri temizle."
        )
        if st.button("Oturum Belgelerini Temizle"):
            st.session_state.session_documents = {}
            st.rerun()
    else:
        st.caption("Henüz bu oturumda dosya yüklenmedi — sorular knowledge base'e (batch CUAD) göre cevaplanacak.")

    if st.button("Sohbeti Temizle (sadece UI)"):
        st.session_state.messages = []
        st.rerun()
    st.caption(
        "Not: Bu, sadece ekrandaki görünümü temizler. Agent'ın kendi hafızası "
        "(db/agent_history.db) ayrı tutulur, yeni bir `session_id` ile yeni "
        "bir sohbet başlatmak için sayfayı tamamen yenile."
    )