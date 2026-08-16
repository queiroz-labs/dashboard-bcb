import pandas as pd
import requests

SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json"


def fetch_sgs(
    code: int,
    name: str | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> pd.DataFrame:
    url = SGS_URL.format(code=code)
    params = []
    if data_inicial:
        params.append(f"dataInicial={data_inicial}")
    if data_final:
        params.append(f"dataFinal={data_final}")
    if params:
        url += "&" + "&".join(params)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return _parse_payload(r.json(), name or f"sgs_{code}")


def _parse_payload(payload: list[dict], name: str) -> pd.DataFrame:
    df = pd.DataFrame(payload)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = df["valor"].astype(str).str.replace(",", ".").astype(float)
    return df.set_index("data").rename(columns={"valor": name})
