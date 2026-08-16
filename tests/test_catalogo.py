import pytest

from src.catalogo import BLOCO_ABERTA, BLOCO_ATIVIDADE, BLOCO_POLITICA, CATALOGO


def test_catalogo_integridade():
    slugs = [s.slug for s in CATALOGO]
    assert len(slugs) == len(set(slugs))
    for s in CATALOGO:
        assert s.nome
        assert s.frequencia in {"D", "M", "T", "A"}
        assert s.unidade
        assert s.contexto
        if s.fonte == "sgs":
            assert isinstance(s.codigo_sgs, int)
        elif s.fonte == "focus":
            assert s.focus_tipo in {"ipca", "selic"}
        elif s.fonte == "sidra":
            assert s.agregado and s.variavel
        else:
            pytest.fail(f"fonte inválida na série {s.slug}: {s.fonte}")


def test_catalogo_blocos_esperados():
    blocos = {s.bloco for s in CATALOGO}
    assert blocos == {BLOCO_ABERTA, BLOCO_ATIVIDADE, BLOCO_POLITICA}
    assert all(
        s.bloco in (BLOCO_ABERTA, BLOCO_ATIVIDADE, BLOCO_POLITICA)
        for s in CATALOGO
    )
