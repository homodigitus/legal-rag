# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# uv'yi resmi imajdan kopyala (hizli kurulum)
COPY --from=ghcr.io/astral-sh/uv:0.4.29 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Sistem bagimliliklari (chromadb / sentence-transformers derleme ihtiyaclari icin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Once sadece bagimlilik tanimlarini kopyala -> layer cache verimliligi
COPY pyproject.toml ./
COPY uv.lock* ./

RUN uv sync --no-install-project --no-dev

# Uygulama kodunu kopyala
COPY . .

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app/streamlit_app.py"]
CMD ["--server.port=8501", "--server.address=0.0.0.0"]
