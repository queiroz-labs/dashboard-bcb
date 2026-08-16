import pandas as pd
import pytest

from src.bcb import _parse_payload, fetch_sgs
from src.metrics import aa_para_am, acumulada_12m, ultima_do_mes

PAYLOAD = [
    {"data": "01/08/1986", "valor": "35,55"},
    {"data": "01/09/1986", "valor": "39,39"},
]


def test_parse_payload():
    df = _parse_payload(PAYLOAD, "selic")
    assert list(df.columns) == ["selic"]
    assert df.index.tolist() == [
        pd.Timestamp("1986-08-01"),
        pd.Timestamp("1986-09-01"),
    ]
    assert df["selic"].tolist() == [35.55, 39.39]


def test_fetch_sgs_selic():
    df = fetch_sgs(4189, name="selic")
    assert not df.empty
    assert list(df.columns) == ["selic"]
    assert df.index.min().year == 1986
    assert isinstance(df["selic"].iloc[-1], float)


def test_fetch_sgs_meta_com_janela():
    df = fetch_sgs(
        432,
        name="meta_selic",
        data_inicial="01/01/2025",
        data_final="31/12/2025",
    )
    assert not df.empty
    assert list(df.columns) == ["meta_selic"]
    assert df.index.min().year >= 2025
    assert isinstance(df["meta_selic"].iloc[-1], float)


def test_acumulada_12m_capitaliza_composto():
    idx = pd.date_range("2024-01-01", periods=13, freq="MS")
    df = pd.DataFrame({"selic": [1.0] * 13}, index=idx)
    acum = acumulada_12m(df, "selic")
    assert acum.iloc[:11].isna().all()
    esperado = ((1.01**12) - 1) * 100
    assert acum.iloc[11] == pytest.approx(esperado)
    assert acum.iloc[12] == pytest.approx(esperado)
    assert acum.iloc[-1] > 12.0


def test_aa_para_am_zero_permanece_zero():
    s = pd.Series([0.0, 0.0])
    out = aa_para_am(s)
    assert (out == 0.0).all()


def test_aa_para_am_ida_e_volta():
    idx = pd.date_range("2025-01-01", periods=13, freq="MS")
    mensais = aa_para_am(pd.Series([13.97] * 13)).values
    df = pd.DataFrame({"selic": mensais}, index=idx)
    acum = acumulada_12m(df, "selic")
    assert acum.iloc[-1] == pytest.approx(13.97)


def test_ultima_do_mes_pega_valor_vigente_no_fim():
    idx = pd.to_datetime(
        [
            "2025-01-05",
            "2025-01-31",
            "2025-02-10",
            "2025-02-20",
            "2025-03-01",
        ]
    )
    df = pd.DataFrame({"meta": [10.5, 10.75, 10.75, 11.25, 11.25]}, index=idx)
    out = ultima_do_mes(df)
    assert out.index.tolist() == [
        pd.Timestamp("2025-01-01"),
        pd.Timestamp("2025-02-01"),
        pd.Timestamp("2025-03-01"),
    ]
    assert out["meta"].tolist() == [10.75, 11.25, 11.25]
