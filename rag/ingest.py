"""
CUAD verisinin yuklenmesi.

Beklenen kaynak yapisi (data/raw/ altina indirilecek):
    data/raw/full_contract_txt/*.txt   -> sozlesmelerin tam metni
    data/raw/CUAD_v1.json              -> SQuAD formatinda soru-cevap etiketleri
    data/raw/master_clauses.csv        -> sozlesme x kloz ozet tablosu

TODO (deneysel calisma sirasinda doldurulacak):
    - [ ] load_contracts(): tum .txt dosyalarini oku, dokuman listesi dondur
    - [ ] load_cuad_qa(): CUAD_v1.json'dan soru-cevap ciftlerini parse et
    - [ ] Metadata: her dokumana contract_id, file_name, source ekle
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from rag.config import settings


@dataclass
class ContractDocument:
    contract_id: str
    file_name: str
    text: str
    metadata: dict


def load_contracts(raw_dir: str | None = None) -> list[ContractDocument]:
    """full_contract_txt/ klasorundeki tum sozlesmeleri yukler.

    TODO: implement
    """
    raw_dir = Path(raw_dir or settings.data_raw_dir)
    txt_dir = raw_dir / "full_contract_txt"
    if not txt_dir.exists():
        raise FileNotFoundError(
            f"{txt_dir} bulunamadi. CUAD_v1.zip'i indirip data/raw/ altina "
            "cikardigindan emin ol (bkz. README.md)."
        )
    raise NotImplementedError("TODO: .txt dosyalarini oku ve ContractDocument listesi don")


def load_cuad_qa(json_path: str | None = None) -> list[dict]:
    """CUAD_v1.json'dan SQuAD formatindaki soru-cevap ciftlerini yukler.

    Bu, RAG sisteminin dogrulugunu test etmek icin kullanilabilir
    (gercek etiketli soru-cevaplarla retrieval sonuclarini karsilastir).

    TODO: implement
    """
    json_path = Path(json_path or settings.cuad_json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"{json_path} bulunamadi.")
    with open(json_path, encoding="utf-8") as f:
        _data = json.load(f)
    raise NotImplementedError("TODO: SQuAD formatini parse et")


if __name__ == "__main__":
    docs = load_contracts()
    print(f"{len(docs)} sozlesme yuklendi.")
