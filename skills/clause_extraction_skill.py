"""
Ornek skill: bir sozlesme metninden belirli kloz turlerini (fesih, gizlilik,
sorumluluk sinirlamasi vb.) cikarmak.

Bu, "ileri vizyon" bolumunde gosterilebilecek bir genisletme fikri.
CUAD'in 41 kloz kategorisinden bir alt kumesiyle baslanabilir.

TODO (zaman kalirsa):
    - [ ] CUAD master_clauses.csv'deki kategori isimlerini referans al
    - [ ] extract_clauses(text, categories) -> {category: [bulunan_pasajlar]}
"""
from __future__ import annotations

DEFAULT_CATEGORIES = [
    "Termination For Convenience",
    "Confidentiality",
    "Limitation Of Liability",
    "Governing Law",
    "Non-Compete",
]


def extract_clauses(text: str, categories: list[str] | None = None) -> dict[str, list[str]]:
    """TODO: implement - retrieval veya LLM tabanli kloz cikarimi."""
    categories = categories or DEFAULT_CATEGORIES
    del text
    raise NotImplementedError("TODO: her kategori icin ilgili pasaji bul")
