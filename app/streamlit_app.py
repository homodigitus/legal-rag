"""
Streamlit Demo - Yerel LLM ile Hukuki Metin Analizi

Calistirmak icin:
    uv run streamlit run app/streamlit_app.py

Beklenen 3 ekran (vaka talimatina gore):
    1. Belge yukleme ekrani
    2. Soru input ekrani
    3. Cevap + kaynak gosterimi
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.config import settings  # noqa: E402

st.set_page_config(
    page_title="Eksun - Hukuki Metin Analizi",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Yerel LLM ile Hukuki Metin Analizi")
st.caption(
    "CUAD sozlesme veri seti uzerinde RAG tabanli soru-cevap. "
    f"Model: `{settings.ollama_model}` (local, Ollama uzerinden calisir)"
)

tab_upload, tab_qa, tab_about = st.tabs(["📄 Belge Yukleme", "❓ Soru-Cevap", "ℹ️ Hakkinda"])

with tab_upload:
    st.subheader("Sozlesme Yukle / Sec")
    st.info("TODO: kullanici .txt/.pdf yukleyebilsin veya CUAD'daki hazir sozlesmelerden secebilsin.")
    uploaded_file = st.file_uploader("Sozlesme dosyasi (.txt / .pdf)", type=["txt", "pdf"])
    if uploaded_file is not None:
        st.success(f"Yuklendi: {uploaded_file.name}")
        # TODO: rag.ingest ile parse et, rag.chunking + db.vectorstore ile indexle
        st.warning("TODO: ingest + chunk + index pipeline'ina bagla")

with tab_qa:
    st.subheader("Sozlesme Hakkinda Soru Sor")
    question = st.text_input(
        "Sorunuz",
        placeholder="Ornek: Bu sozlesmedeki fesih bildirim suresi nedir?",
    )
    if st.button("Sor", type="primary") and question:
        with st.spinner("Yerel LLM ile analiz ediliyor..."):
            # TODO: from rag.pipeline import answer_question
            # result = answer_question(question)
            st.warning("TODO: rag.pipeline.answer_question() ile baglantiyi kur")
            # st.markdown("### Cevap")
            # st.write(result.answer)
            # st.markdown("### Kaynaklar")
            # for src in result.sources:
            #     st.caption(f"- {src}")

with tab_about:
    st.subheader("Sistem Ozeti")
    st.markdown(
        """
        - **Veri seti**: CUAD v1 (Contract Understanding Atticus Dataset) — 510 ticari
          sozlesme, 41 kloz kategorisi, [Kaggle](https://www.kaggle.com/datasets/theatticusproject/atticus-open-contract-dataset-aok-beta)
        - **Embedding**: `sentence-transformers/all-MiniLM-L6-v2` (local, HuggingFace)
        - **Vektor DB**: ChromaDB (local, persist)
        - **LLM**: Ollama uzerinde yerel model (bulut API kullanilmaz — EPDK/on-prem uyumlu tasarim)
        - **Mimari**: ingest -> chunk -> embed -> retrieve -> local LLM -> kaynakli cevap
        """
    )
