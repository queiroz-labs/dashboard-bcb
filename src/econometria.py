import pandas as pd
import statsmodels.api as sm
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


def transformar(serie: pd.Series, tipo: str) -> pd.Series:
    if tipo == "nivel":
        return serie
    if tipo == "var_pct":
        return serie.pct_change() * 100
    if tipo == "diff":
        return serie.diff()
    raise ValueError(f"transformação não suportada: {tipo}")


def correlacionar(a: pd.Series, b: pd.Series, tipo: str = "nivel") -> dict:
    dados = pd.concat([transformar(a, tipo), transformar(b, tipo)], axis=1)
    dados.columns = ["a", "b"]
    dados = dados.dropna()
    return {
        "r": dados["a"].corr(dados["b"]),
        "n": len(dados),
        "dados": dados,
    }


def regressao_simples(x: pd.Series, y: pd.Series, tipo: str = "nivel") -> dict:
    dados = pd.concat([transformar(x, tipo), transformar(y, tipo)], axis=1)
    dados.columns = ["x", "y"]
    dados = dados.dropna()
    X = sm.add_constant(dados["x"])
    modelo = sm.OLS(dados["y"], X).fit()
    return {
        "alpha": modelo.params.iloc[0],
        "beta": modelo.params.iloc[1],
        "r2": modelo.rsquared,
        "p_beta": modelo.pvalues.iloc[1],
        "n": int(modelo.nobs),
        "dados": dados,
    }
