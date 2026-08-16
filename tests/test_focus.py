import pandas as pd

from src.focus import (
    _parse_ipca_snapshot,
    _parse_selic_history,
    _reuniao_key,
)


def test_parse_ipca_snapshot_agrega_duplicatas():
    rows = [
        {"Data": "2026-08-07", "DataReferencia": "09/2026", "Mediana": 0.42},
        {"Data": "2026-08-07", "DataReferencia": "09/2026", "Mediana": 0.46},
        {"Data": "2026-08-07", "DataReferencia": "10/2026", "Mediana": 0.38},
    ]
    df = _parse_ipca_snapshot(rows, "focus_ipca")
    assert df.index.tolist() == [
        pd.Timestamp("2026-09-01"),
        pd.Timestamp("2026-10-01"),
    ]
    assert df["focus_ipca"].tolist() == [0.44, 0.38]


def test_parse_selic_history_agrega_por_data():
    rows = [
        {"Data": "2026-07-31", "Mediana": 12.0},
        {"Data": "2026-07-31", "Mediana": 12.25},
        {"Data": "2026-08-07", "Mediana": 11.75},
    ]
    df = _parse_selic_history(rows, "focus_selic")
    assert df.index.tolist() == [
        pd.Timestamp("2026-07-31"),
        pd.Timestamp("2026-08-07"),
    ]
    assert df["focus_selic"].tolist() == [12.125, 11.75]


def test_reuniao_key_ordena_ano_e_reuniao():
    assert _reuniao_key("R5/2027") > _reuniao_key("R1/2027")
    assert _reuniao_key("R1/2028") > _reuniao_key("R5/2027")
