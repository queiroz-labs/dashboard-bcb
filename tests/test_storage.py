import sqlite3

import pandas as pd

from src import storage
from src.storage import ler_meta, load_series, salvar_meta, save_series


def test_meta_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "teste.db")
    assert ler_meta("abc") is None
    salvar_meta("abc", "16/08/2026 12:00")
    assert ler_meta("abc") == "16/08/2026 12:00"
    salvar_meta("abc", "16/08/2026 13:30")
    assert ler_meta("abc") == "16/08/2026 13:30"


def test_save_series_forca_coluna_data(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "teste.db")
    df = pd.DataFrame(
        {"v": [1.0, 2.0]},
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
    )
    df.index.name = "Date"
    save_series(df, "t")
    carregado = load_series("t")
    assert carregado is not None
    assert carregado.index.tolist() == [
        pd.Timestamp("2026-01-01"),
        pd.Timestamp("2026-01-02"),
    ]


def test_load_series_tabela_legada_sem_data_retorna_none(tmp_path, monkeypatch):
    db = tmp_path / "teste.db"
    monkeypatch.setattr(storage, "DB_PATH", db)
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE legada (Date TEXT, valor REAL)")
        conn.execute(
            "INSERT INTO legada (Date, valor) VALUES ('2026-01-01', 1.0)"
        )
    assert load_series("legada") is None
