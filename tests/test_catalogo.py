import pytest

from src.catalogo import (
    BLOCO_ABERTA,
    BLOCO_ATIVIDADE,
    BLOCO_EXTERNOS,
    BLOCO_MERCADO,
    BLOCO_POLITICA,
    CATALOGO,
)


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
        elif s.fonte == "externo":
            assert s.ticker or s.tipo_derivada
        elif s.fonte == "sidra":
            assert s.agregado and s.variavel
        else:
            pytest.fail(f"fonte inválida na série {s.slug}: {s.fonte}")


def test_catalogo_blocos_esperados():
    blocos = {s.bloco for s in CATALOGO}
    assert blocos == {
        BLOCO_ABERTA,
        BLOCO_ATIVIDADE,
        BLOCO_POLITICA,
        BLOCO_MERCADO,
        BLOCO_EXTERNOS,
    }
    assert all(
        s.bloco
        in (BLOCO_ABERTA, BLOCO_ATIVIDADE, BLOCO_POLITICA, BLOCO_MERCADO, BLOCO_EXTERNOS)
        for s in CATALOGO
    )


def test_unidades_cdi_e_igpm():
    por_slug = {s.slug: s for s in CATALOGO}
    assert por_slug["cdi"].unidade == "% a.d."
    assert por_slug["igpm"].unidade == "% a.m."


def test_unidades_novas_series():
    por_slug = {s.slug: s for s in CATALOGO}

    def conferir(slug, unidade, frequencia, fonte, codigo_sgs=None):
        s = por_slug[slug]
        assert s.unidade == unidade
        assert s.frequencia == frequencia
        assert s.fonte == fonte
        if codigo_sgs is not None:
            assert s.codigo_sgs == codigo_sgs

    conferir("resultado_primario", "% PIB (12m)", "M", "sgs", 5793)
    conferir("resultado_nominal", "% PIB (12m)", "M", "sgs", 5727)
    conferir("divida_bruta_pib", "% PIB", "M", "sgs", 13762)
    conferir("divida_liquida_pib", "% PIB", "M", "sgs", 4513)
    conferir("credito_pib", "% PIB", "M", "sgs", 20622)
    conferir("inadimplencia", "%", "M", "sgs", 21082)
    conferir("concessoes_credito", "R$ milhões", "M", "sgs", 20631)

    desemprego = por_slug["desemprego"]
    assert desemprego.unidade == "%"
    assert desemprego.frequencia == "M"
    assert desemprego.agregado == "6381"
    assert desemprego.variavel == "4099"

    rendimento = por_slug["rendimento_real"]
    assert rendimento.unidade == "R$"
    assert rendimento.frequencia == "T"
    assert rendimento.agregado == "5436"
    assert rendimento.variavel == "5933"
    assert rendimento.classificacoes == {"2": "6794"}


def test_classificacoes_sidra_sao_dict():
    for s in CATALOGO:
        if s.classificacoes is not None:
            assert s.fonte == "sidra"
            assert isinstance(s.classificacoes, dict)
    por_slug = {s.slug: s for s in CATALOGO}
    assert por_slug["desemprego"].classificacoes is None
