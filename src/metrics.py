import numpy as np
import pandas as pd


def acumulada_12m(df: pd.DataFrame, col: str) -> pd.Series:
    taxa = 1 + df[col] / 100
    selic_12m = (
        taxa
        .rolling(window=12, min_periods=12)
        .apply(np.prod, raw=True)
        .sub(1)
        .mul(100)
    )
    return selic_12m


def aa_para_am(serie: pd.Series) -> pd.Series:
    return ((1 + serie / 100) ** (1 / 12) - 1) * 100


def ultima_do_mes(df: pd.DataFrame) -> pd.DataFrame:
    return df.resample("MS").last()


def formatar_periodo(data: pd.Timestamp, frequencia: str) -> str:
    if frequencia == "D":
        return data.strftime("%d/%m/%Y")
    if frequencia == "M":
        return data.strftime("%b/%Y")
    if frequencia == "T":
        trimestre = (data.month - 1) // 3 + 1
        return f"{trimestre}º trimestre de {data.year}"
    return data.strftime("%Y")
