import pandas as pd

from src import externos
from src.externos import cruzamento_brl_jpy, fetch_ticker


def test_fetch_ticker_extrai_close(monkeypatch):
    idx = pd.date_range("2026-01-05", periods=5, freq="B")
    fake = pd.DataFrame(
        {
            "Close": [100.0, 101.0, 102.0, 103.0, 104.0],
            "Open": [99.0] * 5,
        },
        index=idx,
    )
    monkeypatch.setattr(
        externos.yf, "download", lambda *a, **k: fake
    )
    df = fetch_ticker("^BVSP", name="ibovespa")
    assert list(df.columns) == ["ibovespa"]
    assert df["ibovespa"].iloc[-1] == 104.0
    assert str(df.index.tz) == "None"
    assert df.index.name is None


def test_fetch_ticker_lida_com_multiindice(monkeypatch):
    idx = pd.date_range("2026-01-05", periods=3, freq="B")
    fake = pd.DataFrame(
        {( "Close", "^GSPC"): [10.0, 11.0, 12.0]},
        index=idx,
    )
    monkeypatch.setattr(
        externos.yf, "download", lambda *a, **k: fake
    )
    df = fetch_ticker("^GSPC", name="sp500")
    assert df["sp500"].tolist() == [10.0, 11.0, 12.0]


def test_fetch_ticker_sem_dados(monkeypatch):
    monkeypatch.setattr(
        externos.yf, "download", lambda *a, **k: pd.DataFrame()
    )
    try:
        fetch_ticker("NADA", name="x")
    except ValueError:
        pass
    else:
        raise AssertionError("deveria lançar ValueError para ticker sem dados")


def test_cruzamento_brl_jpy():
    ptax = pd.DataFrame(
        {"ptax": [5.0, 5.5]},
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
    )
    usd_jpy = pd.DataFrame(
        {"usd_jpy": [100.0, 110.0]},
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
    )
    out = cruzamento_brl_jpy(ptax, usd_jpy)
    assert list(out.columns) == ["brl_jpy"]
    assert out["brl_jpy"].tolist() == [0.05, 0.05]


def test_roundtrip_save_load_externo(monkeypatch, tmp_path):
    from src import storage
    from src.storage import load_series, save_series

    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "teste.db")
    idx = pd.date_range("2026-01-05", periods=3, freq="B")
    fake = pd.DataFrame({"Close": [10.0, 11.0, 12.0]}, index=idx)
    monkeypatch.setattr(externos.yf, "download", lambda *a, **k: fake)
    df = fetch_ticker("^BVSP", name="ibovespa")
    save_series(df, "ibovespa")
    carregado = load_series("ibovespa")
    assert carregado is not None
    assert list(carregado.columns) == ["ibovespa"]
    assert carregado["ibovespa"].tolist() == [10.0, 11.0, 12.0]
