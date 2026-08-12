# Yerel LLM ile Hukuki Metin Analizi

**Eksun Holding — Büyük Veri ve Yapay Zeka Ekibi — Vaka Çalışması (Proje B)**

CUAD (Contract Understanding Atticus Dataset) üzerinde, tamamen **yerel/on-prem** çalışan bir
RAG (Retrieval-Augmented Generation) mimarisiyle sözleşme sorgulama sistemi. Bulut LLM API'si
kullanılmaz — model, embedding ve vektör veritabanı tamamen local çalışır.

## İçindekiler
- [Neden Yerel Mimari](#neden-yerel-mimari)
- [Mimari](#mimari)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Veri İndirme](#veri-i̇ndirme)
- [Çalıştırma](#çalıştırma)
- [Docker ile Çalıştırma](#docker-ile-çalıştırma)
- [Geliştirme Akışı](#geliştirme-akışı)
- [Yol Haritası / İleri Vizyon](#yol-haritası--i̇leri-vizyon)

## Neden Yerel Mimari

Finans/enerji sektöründe regülasyon (ör. EPDK) gereği hassas veri bulut ortamına
çıkarılamayabilir. Bu proje bu kısıtı gerçekçi bir senaryo olarak ele alır:

| Katman | Teknoloji | Neden Local |
|---|---|---|
| LLM | Ollama (Llama 3.1 8B / Mistral 7B vb.) | Model ağırlıkları makinede, dışarı veri çıkmaz |
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) | İlk indirmeden sonra tamamen offline çalışır |
| Vektör DB | ChromaDB (persistent, local disk) | Bulut vektör servisi kullanılmaz |
| Veri | Disk üzerinde `data/` | Sözleşme metinleri dışarı gönderilmez |

## Mimari

```
Sözleşme (.txt/.pdf)
        │
        ▼
   rag/ingest.py        ← belge yükleme + parse
        │
        ▼
   rag/chunking.py       ← RecursiveCharacterTextSplitter (800/200)
        │
        ▼
   rag/embeddings.py     ← sentence-transformers (local)
        │
        ▼
   db/vectorstore.py     ← ChromaDB (persist, local)
        │
        ▼
   rag/retriever.py      ← similarity search (top-k)
        │
        ▼
   rag/pipeline.py       ← Ollama (local LLM) + kaynaklı cevap
        │
        ▼
   app/streamlit_app.py  ← 3 ekran: yükleme / soru-cevap / kaynak gösterimi
```

`agents/` ve `skills/` klasörleri, basit RAG akışının ötesine geçmek istersen
(çoklu-adım analiz, kloz çıkarımı gibi) genişletme alanı olarak hazırlandı —
zorunlu değil, zaman kalırsa "ileri vizyon" bölümünde gösterilebilir.

## Proje Yapısı

```
legal-rag/
├── app/                    # Streamlit demo uygulaması
│   ├── streamlit_app.py    # Ana giriş noktası
│   ├── pages/               # (opsiyonel) çoklu sayfa
│   └── components/          # (opsiyonel) paylaşılan UI parçaları
├── rag/                    # RAG çekirdek pipeline
│   ├── config.py            # .env tabanlı merkezi ayarlar
│   ├── ingest.py             # CUAD sözleşmelerini yükleme
│   ├── chunking.py           # Metin parçalama
│   ├── embeddings.py         # Local embedding modeli
│   ├── retriever.py          # Semantic search
│   └── pipeline.py           # Uçtan uca soru-cevap
├── db/                     # Vektör veritabanı katmanı
│   └── vectorstore.py        # ChromaDB wrapper
├── agents/                 # (opsiyonel) agentic genişletme
├── skills/                  # (opsiyonel) tekil yetenekler (kloz çıkarımı vb.)
├── notebooks/               # Deneysel çalışma alanı
│   └── 01_eda_and_prototype.ipynb
├── scripts/
│   └── download_data.py      # Veri indirme/doğrulama yardımcı script
├── data/
│   ├── raw/                  # CUAD ham veri (git'e girmez)
│   └── processed/            # İşlenmiş ara veri (git'e girmez)
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml           # uv paket yönetimi
├── .env.example
└── README.md
```

## Kurulum

### Gereksinimler
- Python 3.12
- [uv](https://docs.astral.sh/uv/) (paket yöneticisi)
- [Ollama](https://ollama.com/) (yerel LLM çalıştırmak için)
- (Opsiyonel) Docker + Docker Compose

### 1. uv kurulumu (yoksa)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Bağımlılıkları kur
```bash
cd legal-rag
uv sync              # sadece runtime bağımlılıkları
uv sync --all-extras # dev bağımlılıkları da (jupyter, pytest, ruff) dahil
```

### 3. Ortam dosyasını hazırla
```bash
cp .env.example .env
# gerekirse OLLAMA_MODEL, CHUNK_SIZE vb. değerleri düzenle
```

### 4. Ollama'yı kur ve modeli indir
```bash
# https://ollama.com/download üzerinden kur, sonra:
ollama pull llama3.1:8b     # veya daha hafif: llama3.2:3b, mistral:7b
ollama serve                 # arka planda çalışır, default port 11434
```

## Veri İndirme

CUAD v1 verisini `data/raw/` altına indir. İki kaynak var:

**Kaggle (talimatta istenen link — önerilen):**
```bash
uv run pip install kaggle   # veya: uv add --dev kaggle
# kaggle.com/settings -> API -> Create New Token -> ~/.kaggle/kaggle.json
kaggle datasets download -d theatticusproject/atticus-open-contract-dataset-aok-beta \
    -p data/raw --unzip
```

**Zenodo (orijinal kaynak, referans için):**
```bash
curl -L -o data/raw/CUAD_v1.zip \
    "https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1"
unzip data/raw/CUAD_v1.zip -d data/raw/
```

İndirmeyi doğrula:
```bash
uv run python scripts/download_data.py
```

Beklenen yapı:
```
data/raw/
├── full_contract_txt/    # 510 sözleşme (.txt)
├── CUAD_v1.json           # SQuAD formatında soru-cevap etiketleri
└── master_clauses.csv     # sözleşme x kloz özet tablosu
```

## Çalıştırma

### Notebook ile deneysel çalışma
```bash
uv run jupyter notebook notebooks/01_eda_and_prototype.ipynb
```

### Streamlit demo
```bash
uv run streamlit run app/streamlit_app.py
```
Tarayıcıda `http://localhost:8501` açılır.

### Testler
```bash
uv run pytest
```

## Docker ile Çalıştırma

`docker-compose.yml`, uygulamayı ve (isteğe bağlı) Ollama'yı birlikte ayağa kaldırır.

```bash
cp .env.example .env
docker compose up --build
```

- App: `http://localhost:8501`
- Ollama: `http://localhost:11434`

> Not: Host makinende zaten Ollama çalışıyorsa, `docker-compose.yml`'deki `ollama`
> servisini kaldırıp `.env` içindeki `OLLAMA_BASE_URL`'i
> `http://host.docker.internal:11434` olarak bırakabilirsin.

## Geliştirme Akışı

Bu repo bilinçli olarak **iskelet + TODO** yapısında bırakıldı — asıl RAG mantığı
`notebooks/01_eda_and_prototype.ipynb` içinde deneysel olarak geliştirilip, olgunlaştıkça
`rag/`, `db/` modüllerine taşınacak. Önerilen sıra:

1. `scripts/download_data.py` ile veriyi doğrula
2. Notebook'ta `rag/ingest.py` → `load_contracts()` fonksiyonunu doldur
3. Notebook'ta chunking'i dene, `rag/chunking.py` → `chunk_documents()`'i doldur
4. `db/vectorstore.py` → `add_chunks()` ile ChromaDB'ye yaz
5. `rag/retriever.py` → `retrieve()` ile semantic search'i doğrula
6. `rag/pipeline.py` → `answer_question()` ile local LLM'i bağla
7. `app/streamlit_app.py` içindeki `TODO` yorumlarını `rag.pipeline.answer_question()`
   çağrısıyla değiştir

## Yol Haritası / İleri Vizyon

- **Hybrid search**: keyword pre-filter + semantic search (büyük sözleşme setlerinde hız)
- **Kloz bazlı çıkarım** (`skills/clause_extraction_skill.py`): CUAD'ın 41 kategorisinden
  seçilenler için otomatik tespit
- **Çoklu-agent mimari** (`agents/`): sorgu yönlendirme (QA / özet / kloz kontrolü)
  ayrı agent'lara bölünebilir
- **Değerlendirme**: `CUAD_v1.json` içindeki etiketli soru-cevaplarla retrieval
  doğruluğunun otomatik ölçülmesi
- **On-prem GPU**: embedding ve LLM inference'ı H200/Blackwell gibi kurumsal GPU
  altyapısına taşıma (bu repo CPU/local geliştirme için tasarlandı, production'da
  `EMBEDDING_DEVICE=cuda` ve GPU'lu bir Ollama/vLLM deployment'ına geçilebilir)

## Veri Kaynağı ve Atıf

Contract Understanding Atticus Dataset (CUAD) v1 — The Atticus Project, CC BY 4.0.
- Zenodo: https://zenodo.org/records/4595826
- Kaggle: https://www.kaggle.com/datasets/theatticusproject/atticus-open-contract-dataset-aok-beta
- Makale: Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review", 2021
