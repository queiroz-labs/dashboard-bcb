from src import storage
from src.storage import ler_meta, salvar_meta


def test_meta_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "teste.db")
    assert ler_meta("abc") is None
    salvar_meta("abc", "16/08/2026 12:00")
    assert ler_meta("abc") == "16/08/2026 12:00"
    salvar_meta("abc", "16/08/2026 13:30")
    assert ler_meta("abc") == "16/08/2026 13:30"
