import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller


def decompor(df: pd.DataFrame, col: str) -> dict[str, pd.Series]:
    serie = df[col].dropna()
    serie = serie.asfreq("MS")
    decomp = seasonal_decompose(serie, model="additive", period=12)
    return {
        "trend": decomp.trend,
        "seasonal": decomp.seasonal,
        "resid": decomp.resid,
    }


def rodar_adf(serie: pd.Series) -> dict[str, dict]:
    s = serie.dropna()

    def rodar(dados: pd.Series) -> dict:
        resultado = adfuller(dados, autolag="AIC")
        stat, p = resultado[0], resultado[1]
        criticos = resultado[4]
        return {
            "stat": stat,
            "p": p,
            "criticos": criticos,
            "estacionaria": bool(p < 0.05),
        }

    return {
        "nivel": rodar(s),
        "dif": rodar(s.diff().dropna()),
    }
