"""
CUAD veri setini indirmek icin yardimci script.

Vaka talimati Kaggle linki istedigi icin Kaggle CLI onerilir:

    pip install kaggle  (veya uv ile: uv add --dev kaggle)
    # ~/.kaggle/kaggle.json icinde API anahtarin olmali (kaggle.com/settings)
    kaggle datasets download -d theatticusproject/atticus-open-contract-dataset-aok-beta -p data/raw --unzip

Alternatif (orijinal kaynak, Zenodo):
    https://zenodo.org/records/4595826  (CUAD_v1.zip, 105.9 MB, CC BY 4.0)
    curl -L -o data/raw/CUAD_v1.zip "https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1"
    unzip data/raw/CUAD_v1.zip -d data/raw/

Bu script, indirilen zip'in beklenen yapida olup olmadigini dogrular.
"""
from __future__ import annotations

from pathlib import Path

from rag.config import settings

EXPECTED_PATHS = [
    "full_contract_txt",
    "CUAD_v1.json",
    "master_clauses.csv",
]


def verify_data_dir(raw_dir: str | None = None) -> None:
    raw_dir = Path(raw_dir or settings.data_raw_dir)
    print(f"Kontrol ediliyor: {raw_dir.resolve()}")
    missing = []
    for name in EXPECTED_PATHS:
        p = raw_dir / name
        status = "OK" if p.exists() else "EKSIK"
        print(f"  [{status}] {name}")
        if not p.exists():
            missing.append(name)

    if missing:
        print(
            "\nBazi dosyalar eksik. README.md 'Kurulum > Veri Indirme' bolumune bak."
        )
    else:
        n_contracts = len(list((raw_dir / "full_contract_txt").glob("*.txt")))
        print(f"\nTum dosyalar mevcut. {n_contracts} sozlesme bulundu.")


if __name__ == "__main__":
    verify_data_dir()
