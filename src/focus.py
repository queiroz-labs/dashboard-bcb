from urllib.parse import urlencode

import pandas as pd
import requests

FOCUS_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
)


def fetch_focus(tipo: str, name: str | None = None) -> pd.DataFrame:
    if tipo == "ipca":
        return _fetch_focus_ipca(name or "focus_ipca")
    if tipo == "selic":
        return _fetch_focus_selic(name or "focus_selic")
    raise ValueError(f"tipo Focus não suportado: {tipo}")


def _fetch_focus_ipca(name: str) -> pd.DataFrame:
    rows = _request(
        "ExpectativaMercadoMensais",
        {
            "$top": 1000,
            "$filter": "Indicador eq 'IPCA'",
            "$select": "Indicador,Data,DataReferencia,Mediana",
            "$orderby": "Data desc",
        },
    )
    latest_date = max(row["Data"] for row in rows)
    snapshot = [row for row in rows if row["Data"] == latest_date]
    return _parse_ipca_snapshot(snapshot, name)


def _fetch_focus_selic(name: str) -> pd.DataFrame:
    resource = "ExpectativasMercadoSelic"
    rows = _request(
        resource,
        {
            "$top": 500,
            "$filter": "Indicador eq 'Selic'",
            "$select": "Indicador,Data,Reuniao,Mediana",
            "$orderby": "Data desc",
        },
    )
    latest_date = max(row["Data"] for row in rows)
    snapshot = [row for row in rows if row["Data"] == latest_date]
    reunioes = sorted(
        {row["Reuniao"] for row in snapshot if row.get("Reuniao")},
        key=_reuniao_key,
    )
    if not reunioes:
        return _parse_selic_history(snapshot, name)

    reuniao = reunioes[0].replace("'", "''")
    history = _request(
        resource,
        {
            "$top": 1000,
            "$filter": f"Indicador eq 'Selic' and Reuniao eq '{reuniao}'",
            "$select": "Indicador,Data,Reuniao,Mediana",
            "$orderby": "Data asc",
        },
    )
    return _parse_selic_history(history, name)


def _request(resource: str, params: dict) -> list[dict]:
    params = {**params, "$format": "json"}
    query = urlencode(params).replace("+", "%20")
    response = requests.get(f"{FOCUS_URL}{resource}?{query}", timeout=60)
    response.raise_for_status()
    rows = response.json().get("value", [])
    if not rows:
        raise ValueError(f"API Focus não retornou dados para {resource}")
    return rows


def _parse_ipca_snapshot(rows: list[dict], name: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["data"] = df["DataReferencia"].map(_parse_referencia)
    df["valor"] = pd.to_numeric(df["Mediana"], errors="coerce")
    return (
        df.dropna(subset=["data", "valor"])
        .groupby("data", as_index=True)["valor"]
        .median()
        .to_frame(name)
        .sort_index()
    )


def _parse_selic_history(rows: list[dict], name: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["valor"] = pd.to_numeric(df["Mediana"], errors="coerce")
    return (
        df.dropna(subset=["data", "valor"])
        .groupby("data", as_index=True)["valor"]
        .median()
        .to_frame(name)
        .sort_index()
    )


def _parse_referencia(value: str) -> pd.Timestamp:
    if "/" in value:
        return pd.to_datetime(value, format="%m/%Y")
    return pd.to_datetime(value, format="%Y")


def _reuniao_key(value: str) -> tuple[int, int]:
    numero, ano = value.split("/")
    return int(ano), int(numero.removeprefix("R"))
