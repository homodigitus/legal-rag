"""
Agentic katman (opsiyonel genisletme).

Basit RAG QA yeterliyse bu klasoru bos birakabilirsin. Zaman kalirsa
sunuma "ileri vizyon" olarak eklenebilecek agent fikirleri:

    - contract_qa_agent   : tek sozlesme uzerinde soru-cevap (rag/pipeline.py'i sarar)
    - compliance_agent    : sozlesmeyi onceden tanimli kurallara (kloz kontrolu) karsi tarar
    - router_agent        : gelen soruyu QA / compliance / summarization
                             gorevlerinden birine yonlendirir

Ileride Agno/LangGraph gibi bir orkestrasyon framework'u eklenebilir
(Murat'in causalbanking/CoreMemory projelerinde oldugu gibi).
"""
