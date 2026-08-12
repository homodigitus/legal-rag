# Yerel LLM ile Hukuki Metin Analizi

**Eksim Holding — Büyük Veri ve Yapay Zeka Ekibi — Vaka Çalışması (Proje B)**

CUAD (Contract Understanding Atticus Dataset) üzerinde çalışan, tamamen **yerel/on-prem**
bir agentic RAG (Retrieval-Augmented Generation) sistemi. Bulut LLM API'si kullanılmaz —
LLM, embedding ve vektör veritabanı tamamen local çalışır. Sohbet arayüzü tek bir chat
kutusundan hem belge yükleme hem soru sormayı destekler.

## İçindekiler
- [Mimari](#mimari)
- [Neden Bu Tasarım Kararları](#neden-bu-tasarım-kararları)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Veri İndirme](#veri-i̇ndirme)
- [Çalıştırma](#çalıştırma)
- [Docker ile Çalıştırma](#docker-ile-çalıştırma)
- [Yol Haritası / İleri Vizyon](#yol-haritası--i̇leri-vizyon)

## Mimari

```
Belge yükleme (PDF/TXT)
        │
        ▼
Metin çıkarma (pypdf veya doğrudan decode)
        │
        ▼
Metin chunking (LangChain RecursiveCharacterTextSplitter, 800/200)
        │
        ▼
Yerel embedding (Ollama: leoipulsar/harrier-0.6b, 1024 boyut)
        │
        ├──────────────────────┐
        ▼                      ▼
Bu oturumun belgesi     Knowledge base arama
(doğrudan context'e     (ChromaDB, hybrid:
 eklenir, retrieval      keyword + semantic,
 bypass edilir)          search_knowledge=True)
        │                      │
        └──────────┬───────────┘
                    ▼
        Agno Agent + Ollama (gemma4:e2b-it-qat)
        + sohbet geçmişi (SqliteDb, session_id,
          add_history_to_context=True)
                    │
                    ▼
        Streamlit Chat UI (st.chat_input:
        dosya + soru tek input'tan)
```

**İki farklı retrieval yolu bilinçli bir tasarım kararı:**
- **Session'da yüklenen belge** için retrieval'e güvenmek yerine metin doğrudan agent'ın
  context'ine ekleniyor. Küçük/edge bir local modelde (`gemma4:e2b-it-qat`) tool-calling
  tetiklemesi tutarsız olabildiği için bu yol güvenilirliği garantiliyor.
- **Batch yüklenen CUAD verisi** için `search_knowledge=True` ile agent'ın kendi kararıyla
  knowledge base'i sorguladığı gerçek "agentic" akış kullanılıyor.

## Neden Bu Tasarım Kararları

| Katman | Teknoloji | Neden |
|---|---|---|
| Agent framework | Agno | Local model'lere (Ollama) native destek, knowledge + chat history + reasoning tool'ları hazır |
| LLM | Ollama (`gemma4:e2b-it-qat`) | Model ağırlıkları makinede, dışarı veri çıkmaz; edge/düşük kaynaklı senaryo için hızlı |
| Embedding | Ollama (`leoipulsar/harrier-0.6b`, 1024d) | CUAD gibi hukuki metin alanında güçlü performans ([kaynak](https://aimultiple.com/open-source-embedding-models)), tamamen local |
| Vektör DB | ChromaDB, hybrid search | Bulut/pgvector değil; keyword + semantic arama birlikte, ekstra Docker servisi gerektirmez |
| Chat history | Agno `SqliteDb` + `session_id` | Her oturum kendi geçmişini tutar, `add_history_to_context=True` ile bağlam korunur |
| Chunking | LangChain `RecursiveCharacterTextSplitter` | 800 karakter / 200 overlap, klozların ortadan bölünmesini azaltır |
| UI | Streamlit `st.chat_input(accept_file=...)` | Dosya yükleme ve soru sorma tek bir chat akışında, ayrı sekme gerekmez |
| Neden tamamen local | — | EPDK regülasyonu nedeniyle bulut kullanılmayan, on-prem ağırlıklı kurumsal ortamı simüle eder |

## Proje Yapısı

```
eksun-legal-rag/
├── app/
│   └── streamlit_app.py       # Ana giriş noktası — chat tabanlı UI
├── rag/
│   └── config.py                # .env tabanlı merkezi ayarlar (model isimleri, boyutlar, chunk parametreleri)
├── notebooks/
│   └── 01_eda_and_prototype.ipynb # Deneysel çalışma alanı — EDA, ingest, agent testleri
├── scripts/
│   └── download_data.py           # Veri indirme/doğrulama yardımcı script
├── data/
│   ├── raw/                       # CUAD ham veri (git'e girmez)
│   └── processed/                 # İşlenmiş ara veri (git'e girmez)
├── db/                             # ChromaDB persist dizini + agent_history.db (SQLite, git'e girmez)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml                 # uv paket yönetimi
├── .env.example
└── README.md
```

## Kurulum

### Gereksinimler
- Python 3.12
- [uv](https://docs.astral.sh/uv/) (paket yöneticisi)
- [Ollama](https://ollama.com/) (yerel LLM + embedding çalıştırmak için)
- (Opsiyonel) Docker + Docker Compose

### 1. uv kurulumu (yoksa)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Bağımlılıkları kur
```bash
cd eksun-legal-rag
uv sync
```

### 3. Ortam dosyasını hazırla
```bash
cp .env.example .env
```

### 4. Ollama'yı kur, LLM ve embedding modellerini indir
```bash
ollama pull gemma4:e2b-it-qat        # local LLM
ollama pull leoipulsar/harrier-0.6b  # local embedding
ollama serve                          # arka planda çalışır, default port 11434
```

## Veri İndirme

CUAD v1 verisini `data/raw/` altına indir. İki kaynak var:

**Kaggle (talimatta istenen link — önerilen):**
```bash
uv run pip install kaggle
kaggle datasets download -d theatticusproject/atticus-open-contract-dataset-aok-beta \
    -p data/raw --unzip
```

**Zenodo (orijinal kaynak, referans için):**
```bash
curl -L -o data/raw/CUAD_v1.zip \
    "https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1"
unzip data/raw/CUAD_v1.zip -d data/raw/
```

## Çalıştırma

### Notebook ile deneysel çalışma
```bash
uv run jupyter notebook notebooks/01_eda_and_prototype.ipynb
```
Notebook, `CUAD_v1.json`'daki paragrafları chunk'layıp embed edip ChromaDB'ye (batch,
`cuad_contracts` collection'ı) yazan ve ardından Agno agent ile örnek sorular soran akışı
gösterir.

### Streamlit demo
```bash
uv run streamlit run app/streamlit_app.py
```
Tarayıcıda `http://localhost:8501` açılır. Chat kutusundan hem `.txt`/`.pdf` belge
yükleyebilir hem soru sorabilirsin — aynı submit'te ikisi de olabilir.

## Docker ile Çalıştırma

```bash
cp .env.example .env
docker compose up --build
```

`ollama-init` servisi, `ollama` servisi ayağa kalktıktan sonra gerekli LLM ve embedding
modellerini otomatik çeker; `app` servisi bu iş bitene kadar bekler. İlk çalıştırmada model
indirme süresi nedeniyle birkaç dakika sürebilir.

- App: `http://localhost:8501`
- Ollama: `http://localhost:11434`

`db/` klasörü host'a mount edilir — ChromaDB verisi ve `agent_history.db` (sohbet geçmişi)
container yeniden başlatıldığında kaybolmaz.

## Yol Haritası / İleri Vizyon

- **Kloz uyumluluk kontrolü**: CUAD'ın resmi 41 kategorisine dayanan hybrid (keyword +
  local LLM) bir kontrol katmanı eklenebilir
- **Çoklu-agent mimari**: sorgu yönlendirme (QA / özet / kloz kontrolü) ayrı agent'lara
  bölünebilir
- **Değerlendirme**: `CUAD_v1.json` içindeki etiketli soru-cevaplarla retrieval doğruluğunun
  otomatik ölçülmesi
- **Daha güçlü local model**: `gemma4:e2b-it-qat` edge/düşük kaynaklı senaryo için seçildi;
  production'da `gemma4:e4b-it-qat` veya daha büyük bir modelle tool-calling güvenilirliği
  artırılabilir, GPU'lu bir Ollama/vLLM deployment'ına geçilebilir (H200/Blackwell gibi
  kurumsal altyapıda)
- **Agent Harness ve Loop**: Şimdilik basit düzeyde chat history ve reasoning özellikleri eklendi. Fakat guardrails, skill, memory gibi daha ileri agentic bileşenler eklenebilir.

## Veri Kaynağı ve Atıf

Contract Understanding Atticus Dataset (CUAD) v1 — The Atticus Project, CC BY 4.0.
- Zenodo: https://zenodo.org/records/4595826
- Kaggle: https://www.kaggle.com/datasets/theatticusproject/atticus-open-contract-dataset-aok-beta
- Makale: Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review", 2021

Embedding modeli seçimi, CUAD dahil çoklu-domain açık kaynak embedding benchmarkına
dayanmaktadır: https://aimultiple.com/open-source-embedding-models