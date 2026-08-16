import pandas as pd
import yfinance as yf


def fetch_ticker(ticker: str, name: str | None = None) -> pd.DataFrame:
    dados = yf.download(ticker, period="10y", auto_adjust=True, progress=False)
    if dados is None or dados.empty:
        raise ValueError(f"sem dados para o ticker {ticker}")
    fechamento = dados["Close"]
    if isinstance(fechamento, pd.DataFrame):
        fechamento = fechamento.iloc[:, 0]
    fechamento = fechamento.copy()
    fechamento.index = pd.to_datetime(fechamento.index)
    fechamento.index = fechamento.index.tz_localize(None)
    fechamento.index.name = None
    return fechamento.rename(name or ticker).to_frame()


def cruzamento_brl_jpy(ptax: pd.DataFrame, usd_jpy: pd.DataFrame) -> pd.DataFrame:
    alinhados = pd.concat([ptax, usd_jpy], axis=1, join="inner").dropna()
    brl_jpy = alinhados.iloc[:, 0] / alinhados.iloc[:, 1]
    return brl_jpy.rename("brl_jpy").to_frame()
