import pandas as pd

from src.sidra import _parse_periodo, _parse_resultado, fetch_sidra


def _payload() -> dict:
    return [
        {
            "resultados": [
                {
                    "series": [
                        {
                            "serie": {
                                "202401": "7.1",
                                "202402": "7.0",
                                "202403": "..",
                                "202404": "6.8",
                            }
                        }
                    ]
                }
            ]
        }
    ]


def test_parse_resultado_mensal_ignora_faltantes():
    df = _parse_resultado(_payload(), "desemprego", "M")
    assert list(df.columns) == ["desemprego"]
    assert df.index.tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-04-01"),
    ]
    assert df["desemprego"].tolist() == [7.1, 7.0, 6.8]


def test_parse_periodo_mensal():
    assert _parse_periodo("202407", "M") == pd.Timestamp("2024-07-01")


def test_parse_periodo_trimestral():
    assert _parse_periodo("202402", "T") == pd.Timestamp("2024-04-01")
    assert _parse_periodo("202404", "T") == pd.Timestamp("2024-10-01")


def test_parse_periodo_anual():
    assert _parse_periodo("2024", "A") == pd.Timestamp("2024-01-01")


def test_parse_periodo_frequencia_desconhecida_faz_fallback():
    assert _parse_periodo("2024-07-01", "D") == pd.Timestamp("2024-07-01")


def _payload_com(serie: dict) -> dict:
    return [{"resultados": [{"series": [{"serie": serie}]}]}]


def test_parse_resultado_todos_faltantes_retorna_vazio():
    df = _parse_resultado(
        _payload_com({"202401": "..", "202402": "-", "202403": "..."}), "x", "M"
    )
    assert df.empty


def test_parse_resultado_ignora_valor_nao_numerico():
    df = _parse_resultado(
        _payload_com({"202401": "7.0", "202402": "X", "202403": "6.5"}), "x", "M"
    )
    assert df.index.tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-03-01"),
    ]
    assert df["x"].tolist() == [7.0, 6.5]


def test_parse_resultado_ordena_periodos():
    df = _parse_resultado(
        _payload_com({"202403": "6.5", "202401": "7.0", "202402": "6.8"}), "x", "M"
    )
    assert df.index.tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]


def test_fetch_sidra_monta_url_e_classificacao(monkeypatch):
    import src.sidra as sidra

    chamadas = {}

    class FakeResponse:
        def __init__(self, url):
            self.url = url
            self.text = "{}"

        def raise_for_status(self):
            pass

        def json(self):
            return _payload()

    def fake_get(url, timeout):
        chamadas["url"] = url
        return FakeResponse(url)

    monkeypatch.setattr(sidra.requests, "get", fake_get)
    df = fetch_sidra(
        "5436",
        "5934",
        name="rendimento_real",
        classificacoes={"2": "6794"},
        frequencia="T",
    )
    assert "agregados/5436/periodos/all/variaveis/5934" in chamadas["url"]
    assert "localidades=N1[all]" in chamadas["url"]
    assert "classificacao=2[6794]" in chamadas["url"]
    assert list(df.columns) == ["rendimento_real"]
