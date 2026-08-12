"""Temel smoke testler. `chunk_documents` implement edildikce genisletilecek."""
from rag.chunking import get_splitter


def test_splitter_configured():
    splitter = get_splitter()
    chunks = splitter.split_text("Bu bir test cumlesidir. " * 100)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)
