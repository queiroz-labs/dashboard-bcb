import pandas as pd
import pytest

from src.bcb import _parse_payload, fetch_sgs
from src.metrics import (
    aa_para_am,
    acumulada_12m,
    formatar_periodo,
    ultima_do_mes,
    variacao_interanual,
)

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
    df = fetch_sgs(4390, name="selic_mensal")
    assert not df.empty
    assert list(df.columns) == ["selic_mensal"]
    assert df.index.min().year == 1986
    assert isinstance(df["selic_mensal"].iloc[-1], float)


def test_fetch_sgs_selic_anualizada():
    df = fetch_sgs(4189, name="selic_anual")
    assert not df.empty
    assert list(df.columns) == ["selic_anual"]
    assert df.index.min().year == 1986
    assert isinstance(df["selic_anual"].iloc[-1], float)


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


def test_formatar_periodo():
    assert formatar_periodo(pd.Timestamp("2026-08-14"), "D") == "14/08/2026"
    assert formatar_periodo(pd.Timestamp("2026-07-01"), "M") == "Jul/2026"
    assert formatar_periodo(pd.Timestamp("2026-07-01"), "T") == "3º trimestre de 2026"
    assert formatar_periodo(pd.Timestamp("2026-01-01"), "A") == "2026"


def test_variacao_interanual_mensal():
    idx = pd.date_range("2023-01-01", periods=14, freq="MS")
    s = pd.Series(range(100, 114), index=idx, dtype=float)
    yoy = variacao_interanual(s, "M")
    assert yoy.iloc[:12].isna().all()
    assert yoy.iloc[12] == pytest.approx(12.0)
    assert yoy.iloc[13] == pytest.approx((113 - 101) / 101 * 100)


def test_variacao_interanual_trimestral():
    s = pd.Series([100.0, 110.0, 120.0, 130.0, 140.0])
    yoy = variacao_interanual(s, "T")
    assert yoy.iloc[:4].isna().all()
    assert yoy.iloc[4] == pytest.approx(40.0)


def test_variacao_interanual_anual():
    s = pd.Series([100.0, 110.0, 120.0])
    yoy = variacao_interanual(s, "A")
    assert pd.isna(yoy.iloc[0])
    assert yoy.iloc[1] == pytest.approx(10.0)
    assert yoy.iloc[2] == pytest.approx((120 - 110) / 110 * 100)


def test_variacao_interanual_com_nan():
    idx = pd.date_range("2023-01-01", periods=15, freq="MS")
    s = pd.Series([float(i) for i in range(100, 115)], index=idx)
    s.iloc[13] = float("nan")
    yoy = variacao_interanual(s, "M")
    assert yoy.iloc[12] == pytest.approx(12.0)
    assert pd.isna(yoy.iloc[13])
    assert yoy.iloc[14] == pytest.approx((114 - 102) / 102 * 100)
