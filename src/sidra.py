import pandas as pd
import requests

SIDRA_URL = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/"
    "periodos/{periodos}/variaveis/{variavel}"
)

VALORES_FALTANTES = {"..", "...", "-", "", None}


def fetch_sidra(
    agregado: str,
    variavel: str,
    name: str | None = None,
    localidade: str = "N1[all]",
    classificacoes: dict[str, str] | None = None,
    frequencia: str = "M",
    periodos: str = "all",
) -> pd.DataFrame:
    url = SIDRA_URL.format(agregado=agregado, periodos=periodos, variavel=variavel)
    query = [f"localidades={localidade}"]
    for classe, categoria in (classificacoes or {}).items():
        query.append(f"classificacao={classe}[{categoria}]")
    r = requests.get(f"{url}?{'&'.join(query)}", timeout=60)
    r.raise_for_status()
    return _parse_resultado(r.json(), name or f"sidra_{variavel}", frequencia)


def _parse_resultado(payload, name: str, frequencia: str) -> pd.DataFrame:
    serie = payload[0]["resultados"][0]["series"][0]["serie"]
    dados = []
    for periodo, valor in serie.items():
        if valor in VALORES_FALTANTES:
            continue
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            continue
        dados.append((_parse_periodo(periodo, frequencia), numero))
    df = pd.DataFrame(dados, columns=["data", name]).set_index("data")
    return df.sort_index()


def _parse_periodo(periodo: str, frequencia: str) -> pd.Timestamp:
    if frequencia == "M":
        return pd.to_datetime(periodo, format="%Y%m")
    if frequencia == "T":
        ano = int(periodo[:4])
        trimestre = int(periodo[4:])
        mes = (trimestre - 1) * 3 + 1
        return pd.Timestamp(year=ano, month=mes, day=1)
    if frequencia == "A":
        return pd.Timestamp(year=int(periodo), month=1, day=1)
    return pd.to_datetime(periodo)
