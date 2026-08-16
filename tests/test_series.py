import pytest

from src.bcb import fetch_sgs
from src.catalogo import CATALOGO


@pytest.mark.parametrize("serie", CATALOGO, ids=lambda s: s.slug)
def test_smoke_serie(serie):
    assert serie.fonte == "sgs", f"fonte não suportada em {serie.slug}"
    kwargs = {}
    if serie.frequencia == "D":
        kwargs = {
            "data_inicial": "01/01/2025",
            "data_final": "31/12/2025",
        }
    df = fetch_sgs(serie.codigo_sgs, name=serie.slug, **kwargs)
    assert not df.empty
    assert list(df.columns) == [serie.slug]
