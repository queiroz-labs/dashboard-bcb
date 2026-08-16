import pytest

from src.bcb import fetch_sgs
from src.catalogo import CATALOGO
from src.focus import fetch_focus


@pytest.mark.parametrize("serie", CATALOGO, ids=lambda s: s.slug)
def test_smoke_serie(serie):
    if serie.fonte == "sgs":
        kwargs = {}
        if serie.frequencia == "D":
            kwargs = {
                "data_inicial": "01/01/2025",
                "data_final": "31/12/2025",
            }
        df = fetch_sgs(serie.codigo_sgs, name=serie.slug, **kwargs)
    elif serie.fonte == "focus":
        df = fetch_focus(serie.focus_tipo, name=serie.slug)
    else:
        pytest.fail(f"fonte não suportada em {serie.slug}: {serie.fonte}")
    assert not df.empty
    assert list(df.columns) == [serie.slug]
