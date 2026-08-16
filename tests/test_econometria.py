import numpy as np
import pandas as pd

from src.econometria import decompor, rodar_adf


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
