import numpy as np
import pandas as pd
import pytest

from src.econometria import (
    correlacionar,
    decompor,
    regressao_simples,
    rodar_adf,
    transformar,
)


def test_decompor_extrai_componentes():
    idx = pd.date_range("2020-01-01", periods=48, freq="MS")
    sazonal = 10 * np.sin(2 * np.pi * np.arange(48) / 12)
    serie = 100 + 0.5 * np.arange(48) + sazonal
    df = pd.DataFrame({"v": serie}, index=idx)
    comp = decompor(df, "v")
    assert comp["trend"].notna().sum() > 0
    assert comp["seasonal"].notna().sum() > 0
    assert comp["resid"].notna().sum() > 0
    assert len(comp["seasonal"]) == 48


def test_adf_ruido_branco_e_estacionario():
    rng = np.random.default_rng(42)
    serie = pd.Series(rng.normal(size=200))
    res = rodar_adf(serie)
    assert res["nivel"]["estacionaria"] is True
    assert res["nivel"]["p"] < 0.05


def test_adf_passeio_aleatorio_nao_estacionario():
    rng = np.random.default_rng(42)
    serie = pd.Series(rng.normal(size=200)).cumsum()
    res = rodar_adf(serie)
    assert res["nivel"]["estacionaria"] is False
    assert res["nivel"]["p"] >= 0.05
    assert res["dif"]["estacionaria"] is True


def test_transformar_tipos():
    s = pd.Series([100.0, 110.0, 121.0])
    assert transformar(s, "nivel").tolist() == [100.0, 110.0, 121.0]
    var = transformar(s, "var_pct")
    assert var.iloc[1] == pytest.approx(10.0)
    assert var.iloc[2] == pytest.approx(10.0)
    assert transformar(s, "diff").tolist()[1:] == [10.0, 11.0]


def test_correlacionar_perfeita():
    x = pd.Series(np.arange(50), dtype=float)
    res = correlacionar(x, 2 * x + 1)
    assert res["r"] == pytest.approx(1.0)
    assert res["n"] == 50


def test_correlacionar_desalinha_e_despreza_nan():
    a = pd.Series([1.0, 2.0, 3.0], index=[1, 2, 3])
    b = pd.Series([10.0, 20.0, 30.0], index=[2, 3, 4])
    res = correlacionar(a, b)
    assert res["n"] == 2
    assert res["r"] == pytest.approx(1.0)


def test_regressao_simples_recupera_coeficientes():
    rng = np.random.default_rng(7)
    x = pd.Series(rng.normal(size=100))
    y = 2 * x + 1 + rng.normal(scale=1e-6, size=100)
    res = regressao_simples(x, y)
    assert res["beta"] == pytest.approx(2.0, abs=1e-3)
    assert res["alpha"] == pytest.approx(1.0, abs=1e-3)
    assert res["r2"] == pytest.approx(1.0, abs=1e-3)
    assert res["p_beta"] < 0.05
