import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots

from src.bcb import fetch_sgs
from src.catalogo import CATALOGO, Serie
from src.econometria import (
    correlacionar,
    decompor,
    regressao_simples,
    rodar_adf,
)
from src.externos import cruzamento_brl_jpy, fetch_ticker
from src.focus import fetch_focus
from src.metrics import acumulada_12m, formatar_periodo, ultima_do_mes
from src.storage import ler_meta, load_series, salvar_meta, save_series

st.set_page_config(page_title="Dashboard BCB", layout="wide")

SERIE_SELIC_MENSAL = 4390
NOME_SELIC_MENSAL = "selic_mensal"
TABELA_SELIC_MENSAL = f"sgs_{SERIE_SELIC_MENSAL}"

SERIE_SELIC_ANUAL = 4189
NOME_SELIC_ANUAL = "selic_anual"
TABELA_SELIC_ANUAL = f"sgs_{SERIE_SELIC_ANUAL}"

META_SELIC = 432
TABELA_META = f"sgs_{META_SELIC}"

OPCOES_PERIODO = [
    "Histórico completo",
    "Últimos 20 anos",
    "Últimos 5 anos",
    "Últimos 12 meses",
]
ANOS_POR_OPCAO = {
    "Histórico completo": None,
    "Últimos 20 anos": 20,
    "Últimos 5 anos": 5,
    "Últimos 12 meses": 1,
}


def seletor_periodo() -> pd.Timestamp | None:
    janela = st.selectbox("Período do gráfico", OPCOES_PERIODO, index=2)
    anos = ANOS_POR_OPCAO[janela]
    if anos is None:
        return None
    return pd.Timestamp.today() - pd.DateOffset(years=anos)


def _buscar_ou_cache(tabela: str, baixar, atualizar: bool):
    if not atualizar:
        df = load_series(tabela)
        if df is not None:
            return df, "cache local"
    try:
        df = baixar()
    except Exception:
        df = load_series(tabela)
        if df is None:
            return None, None
        return df, "cache local (API indisponível)"
    save_series(df, tabela)
    salvar_meta(tabela, pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"))
    return df, "API"


def pagina_selic() -> None:
    st.title("Dashboard de Séries Macro — BCB/SGS")
    st.caption("Fase 1 — MVP: SELIC mensal (série 4390 da API SGS)")

    col_btn, _ = st.columns([1, 5])
    atualizar = col_btn.button("Atualizar dados")

    def baixar_selic() -> pd.DataFrame:
        return fetch_sgs(SERIE_SELIC_MENSAL, name=NOME_SELIC_MENSAL)

    def baixar_selic_anual() -> pd.DataFrame:
        return fetch_sgs(SERIE_SELIC_ANUAL, name=NOME_SELIC_ANUAL)

    def baixar_meta() -> pd.DataFrame:
        hoje = pd.Timestamp.today()
        inicio = (hoje - pd.DateOffset(years=10)).strftime("%d/%m/%Y")
        return fetch_sgs(
            META_SELIC,
            name="meta_selic",
            data_inicial=inicio,
            data_final=hoje.strftime("%d/%m/%Y"),
        )

    with st.spinner("Carregando dados da SELIC..."):
        df, origem = _buscar_ou_cache(TABELA_SELIC_MENSAL, baixar_selic, atualizar)
        if df is None:
            st.error("Sem dados: API indisponível e sem cache local.")
            st.stop()
        df_anual, _ = _buscar_ou_cache(
            TABELA_SELIC_ANUAL, baixar_selic_anual, atualizar
        )
        meta, _ = _buscar_ou_cache(TABELA_META, baixar_meta, atualizar)

    st.success(
        f"Fonte: {origem} · última atualização: {ler_meta(TABELA_SELIC_MENSAL) or 'nunca'} · "
        f"{len(df)} observações · {df.index.min():%b/%Y} a {df.index.max():%b/%Y}"
    )

    ultimo = df.iloc[-1, 0]
    anterior = df.iloc[-2, 0]
    acum12 = acumulada_12m(df, NOME_SELIC_MENSAL)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "SELIC efetiva no mês",
        f"{ultimo:.2f}% a.m.",
        delta=f"{ultimo - anterior:+.2f} p.p.",
        help=f"Taxa efetiva acumulada no mês (série 4390). Última divulgação: {df.index[-1]:%b/%Y}",
    )
    if meta is not None:
        c2.metric(
            "Meta SELIC (Copom)",
            f"{meta.iloc[-1, 0]:.2f}% a.a.",
            help=f"Taxa-alvo definida pelo Copom, em % a.a. (série 432). Vigência: {meta.index[-1]:%d/%m/%Y}",
        )
    else:
        c2.metric("Meta SELIC (Copom)", "—")
    c3.metric(
        "SELIC efetiva em 12 meses",
        f"{acum12.iloc[-1]:.2f}%",
        help="Capitalização composta das taxas mensais dos últimos 12 meses: (1+r1)×…×(1+r12)−1",
    )
    pos_real = df[df.index >= "1995-01-01"]
    c4.metric(
        "Máxima pós-Plano Real",
        f"{pos_real.iloc[:, 0].max():.2f}% a.m.",
        help=f"Em {pos_real.iloc[:, 0].idxmax():%b/%Y} (desde 1995)",
    )

    corte = seletor_periodo()

    COL_META = "Meta SELIC (Copom) % a.a."
    COL_AM = "Taxa efetiva mensal % a.m."
    COL_AA = "Taxa efetiva anual % a.a."

    linhas_plot = {
        COL_AM: df.rename(columns={NOME_SELIC_MENSAL: COL_AM}),
    }
    if df_anual is not None:
        linhas_plot[COL_AA] = df_anual.rename(columns={NOME_SELIC_ANUAL: COL_AA})
    if meta is not None:
        linhas_plot[COL_META] = ultima_do_mes(meta).rename(
            columns={"meta_selic": COL_META}
        )
    base_plot = pd.concat(linhas_plot.values(), axis=1).sort_index()

    opcoes = list(linhas_plot)
    padrao = [COL_META] if meta is not None else [COL_AM]
    selecionadas = st.multiselect("Linhas do gráfico", opcoes, default=padrao)

    dados = base_plot if corte is None else base_plot[base_plot.index >= corte]

    fig = px.line(
        dados,
        x=dados.index,
        y=selecionadas,
        title="SELIC — meta do Copom e taxas efetivas",
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Taxa (%)",
        title_x=0.25,
        height=480,
        margin=dict(l=0, r=0, t=50, b=0),
        legend_title_text="",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Meta e taxa efetiva anual em % a.a.; taxa efetiva mensal em % a.m.")

    with st.expander("Contexto — o que é a SELIC?", expanded=True):
        st.markdown(
            """
**SELIC** (Sistema Especial de Liquidação e Custódia) é a **taxa básica de juros da economia
brasileira**. É preciso distinguir duas taxas com nomes parecidos:

- **Meta SELIC (série 432, % a.a.):** a taxa-alvo **anual** definida pelo Copom (Comitê de Política
Monetária do Banco Central), em reuniões a cada 45 dias. É o número que sai no noticiário
("Copom mantém a SELIC em X% ao ano").
- **Taxa efetiva mensal (série 4390):** o resultado da capitalização **diária** dos empréstimos
de 1 dia entre bancos lastreados em títulos públicos ao longo do mês. O BCB administra a liquidez
pra que essa taxa efetiva fique perto da meta.
- **Taxa efetiva anualizada (série 4189):** a mesma taxa mensal expressa em `% a.a.` pela
anualização de base 252. Ela aparece como linha opcional no gráfico; não é convertida novamente.

**Conversão mês ↔ ano:** juros compostos, não soma nem multiplicação por 12:
`(1 + i_a.a.) = (1 + i_a.m.)^12`. Por isso a métrica "12 meses" usa capitalização
composta — somar as taxas mensais (como num regime simples) é conceitualmente errado.
O dashboard usa as duas séries oficiais em suas unidades nativas, sem converter a 4189 para mensal:
4390 já é `% a.m.` e 4189 já é `% a.a.` anualizada em base 252.

- **Quem publica:** Banco Central do Brasil — API SGS. 432 é diária (meta), 4390 é mensal desde 1986
e 4189 é mensal anualizada em base 252.
- **Por que importa:** é o principal instrumento de política monetária. Subir a SELIC encarece o crédito,
esfria a demanda e derruba a inflação (canal de transmissão: taxa básica → crédito → consumo → preços).
A SELIC é o piso da estrutura de juros: CDI, financiamentos, títulos públicos e câmbio dependem dela.
- **Onde cai no edital:** política monetária — metas de inflação, instrumentos do BCB e mecanismo de transmissão.

> **Leitura do gráfico:** os picos absurdos de 1989-1994 refletem a hiperinflação e os Planos Collor I/II;
> a queda após julho/1994 é o Plano Real; os ciclos recentes mostram o aperto/afrouxamento do Copom.
> A linha da meta só cobre os últimos ~10 anos (limite da API pra séries diárias); as linhas da 4390
> cobrem desde 1986. É possível adicionar/remover linhas no seletor acima do gráfico.
            """
        )


def _baixar_serie(serie: Serie) -> pd.DataFrame:
    if serie.fonte == "focus":
        df = fetch_focus(serie.focus_tipo, name=serie.slug)
    elif serie.fonte == "externo":
        if serie.tipo_derivada == "brl_jpy":
            hoje = pd.Timestamp.today()
            inicio = (hoje - pd.DateOffset(years=10)).strftime("%d/%m/%Y")
            ptax = fetch_sgs(
                1,
                name="ptax",
                data_inicial=inicio,
                data_final=hoje.strftime("%d/%m/%Y"),
            )
            usd_jpy = fetch_ticker("JPY=X", name="usd_jpy")
            df = cruzamento_brl_jpy(ptax, usd_jpy)
        else:
            df = fetch_ticker(serie.ticker, name=serie.slug)
    elif serie.fonte == "sgs" and serie.frequencia == "D":
        hoje = pd.Timestamp.today()
        inicio = (hoje - pd.DateOffset(years=10)).strftime("%d/%m/%Y")
        df = fetch_sgs(
            serie.codigo_sgs,
            name=serie.slug,
            data_inicial=inicio,
            data_final=hoje.strftime("%d/%m/%Y"),
        )
    elif serie.fonte == "sgs":
        df = fetch_sgs(serie.codigo_sgs, name=serie.slug)
    else:
        raise ValueError(f"fonte não suportada: {serie.fonte}")
    save_series(df, serie.slug)
    return df


def carregar_serie(
    serie: Serie, atualizar: bool = False
) -> tuple[pd.DataFrame | None, str | None]:
    return _buscar_ou_cache(serie.slug, lambda: _baixar_serie(serie), atualizar)


def pagina_explorador() -> None:
    st.title("Explorador de séries")
    st.caption(
        "Fase 2 — blocos: Macroeconomia Aberta, Atividade/PIB, "
        "Política Monetária e Mercado de Capitais"
    )

    blocos = sorted({s.bloco for s in CATALOGO})
    seletor_bloco, seletor_serie, botao_atualizar = st.columns([1, 1, 0.5])
    bloco = seletor_bloco.selectbox("Bloco", blocos)
    series_bloco = [s for s in CATALOGO if s.bloco == bloco]
    por_nome = {s.nome: s for s in series_bloco}
    nome = seletor_serie.selectbox("Série", list(por_nome))
    serie = por_nome[nome]
    atualizar = botao_atualizar.button("Atualizar dados")

    with st.spinner(f"Carregando {serie.nome}..."):
        df, origem = carregar_serie(serie, atualizar)

    if df is None:
        st.error("Sem dados: API indisponível e sem cache local.")
        st.stop()

    st.success(
        f"Fonte: {origem} · última atualização: {ler_meta(serie.slug) or 'nunca'} · "
        f"{len(df)} observações · {df.index.min():%b/%Y} a {df.index.max():%b/%Y}"
    )

    col = serie.slug
    ultimo = df.iloc[-1, 0]
    anterior = df.iloc[-2, 0] if len(df) > 1 else None

    c1, c2 = st.columns(2)
    c1.metric(
        f"{serie.nome} — último valor",
        f"{ultimo:,.2f}".replace(",", " ") + f" {serie.unidade}",
        help=(
            f"Última divulgação: {formatar_periodo(df.index[-1], serie.frequencia)}"
        ),
    )
    if anterior is not None:
        c2.metric(
            f"Variação vs. {formatar_periodo(df.index[-2], serie.frequencia)}",
            f"{ultimo - anterior:+,.2f}".replace(",", " "),
            help=(
                f"Compara {formatar_periodo(df.index[-1], serie.frequencia)} "
                f"com {formatar_periodo(df.index[-2], serie.frequencia)}"
            ),
        )

    dados = df
    if serie.frequencia == "D":
        agregar = st.checkbox(
            "Agregar mensal (último valor do mês)",
            value=False,
            help="A série é diária; marcado, cada mês é representado pelo valor vigente no fim do mês",
        )
        if agregar:
            dados = ultima_do_mes(df)
    if serie.acumulavel and st.checkbox(
        "Acumulado 12 meses (capitalização composta)", value=False
    ):
        dados = dados.copy()
        dados[col] = acumulada_12m(dados, col)

    corte = seletor_periodo()
    dados = dados if corte is None else dados[dados.index >= corte]

    fig = px.line(
        dados,
        x=dados.index,
        y=col,
        title=f"{serie.nome} ({serie.unidade})",
    )
    formato_eixo = {"D": "%d/%m/%Y", "M": "%b/%Y", "T": "%b/%Y", "A": "%Y"}[
        serie.frequencia
    ]
    fig.update_traces(hovertemplate=f"%{{x|{formato_eixo}}}: %{{y:.2f}}")
    fig.update_layout(
        xaxis_title="",
        xaxis_tickformat=formato_eixo,
        yaxis_title=serie.unidade,
        title_x=0.25,
        height=480,
        margin=dict(l=0, r=0, t=50, b=0),
        legend_title_text="",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

    with st.expander(f"Contexto — {serie.nome}", expanded=True):
        st.markdown(serie.contexto)


def _mensalizar(df: pd.DataFrame, serie: Serie) -> pd.DataFrame:
    if serie.frequencia == "D":
        return ultima_do_mes(df)
    return df


def pagina_analises() -> None:
    st.title("Análises — Estatística/Econometria")
    st.caption("Fase 3 — decomposição, ADF, correlação e regressão")

    analise = st.radio(
        "Análise",
        ["Decomposição", "Teste ADF", "Correlação", "Regressão"],
        horizontal=True,
    )

    transformacoes = {
        "nível": "nivel",
        "variação %": "var_pct",
        "1ª diferença": "diff",
    }

    if analise in ("Decomposição", "Teste ADF"):
        mensais = [s for s in CATALOGO if s.frequencia == "M"]
        por_nome = {s.nome: s for s in mensais}
        sel_serie, botao_atualizar = st.columns([4, 1])
        serie = por_nome[sel_serie.selectbox("Série", list(por_nome))]
        atualizar = botao_atualizar.button("Atualizar dados")

        with st.spinner(f"Carregando {serie.nome}..."):
            df, _ = carregar_serie(serie, atualizar)

        if df is None:
            st.error("Sem dados: API indisponível e sem cache local.")
            st.stop()

        col = serie.slug

        if analise == "Decomposição":
            if df[col].notna().sum() < 24:
                st.warning("A série precisa de pelo menos 24 observações mensais.")
                st.stop()
            comp = decompor(df, col)
            fig = make_subplots(
                rows=4,
                cols=1,
                shared_xaxes=True,
                subplot_titles=[
                    "Série observada",
                    "Tendência",
                    "Sazonalidade",
                    "Resíduo",
                ],
            )
            for row, (titulo, dados) in enumerate(
                [
                    (col, df[col]),
                    ("tendência", comp["trend"]),
                    ("sazonalidade", comp["seasonal"]),
                    ("resíduo", comp["resid"]),
                ],
                start=1,
            ):
                fig.add_scatter(
                    x=dados.index, y=dados, mode="lines", name=titulo, row=row, col=1
                )
            fig.update_layout(
                height=760,
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=False,
            )
            st.plotly_chart(fig, width="stretch")
            st.markdown(
                """
**Decomposição aditiva:** Y = T + S + R.

- **Tendência (T):** movimento de longo prazo da série (ex.: queda estrutural da inflação após o Plano Real).
- **Sazonalidade (S):** padrão que se repete a cada 12 meses (ex.: IPCA pressionado por alimentação no início do ano; atividade mais fraca no 1º trimestre).
- **Resíduo (R):** o que sobra — choques pontuais e ruído; o componente usado em diagnósticos de outliers.

> **Por que importa:** dessazonalizar é pré-requisito pra comparar variações de períodos vizinhos e pra modelar.
> **Onde cai no edital:** séries temporais — componentes, ajuste sazonal e dessazonalização.
                """
            )
        else:
            res = rodar_adf(df[col])
            tabela = pd.DataFrame(
                [
                    {
                        "Série": titulo,
                        "Estatística ADF": f"{d['stat']:.3f}",
                        "p-valor": f"{d['p']:.4f}",
                        "Crítico 5%": f"{d['criticos']['5%']:.3f}",
                        "Conclusão": (
                            "estacionária"
                            if d["estacionaria"]
                            else "não estacionária"
                        ),
                    }
                    for titulo, d in [
                        ("nível", res["nivel"]),
                        ("1ª diferença", res["dif"]),
                    ]
                ]
            )
            st.dataframe(tabela, hide_index=True, width="stretch")
            st.markdown(
                """
**Teste de Dickey-Fuller aumentado (ADF):**

- **H0:** a série tem raiz unitária (é não estacionária). p-valor < 5% rejeita H0 → estacionária.
- Se o nível é não estacionário e a 1ª diferença é estacionária, a série é integrada de ordem 1 — I(1).
- Séries econômicas em nível (PIB, IBC-Br) costumam ser I(1); variações percentuais (IPCA mensal) tendem a ser estacionárias.

> **Por que importa:** modelar série não estacionária em nível produz regressão espúria; a ordem de integração define a transformação correta.
> **Onde cai no edital:** econometria — raiz unitária, estacionariedade e ordem de integração.
                """
            )
        return

    todas = {s.nome: s for s in CATALOGO}
    nomes = list(todas)

    if analise == "Correlação":
        sel_a, sel_b, sel_t, botao_atualizar = st.columns([1, 1, 0.7, 0.5])
        serie_a = todas[sel_a.selectbox("Série A", nomes)]
        indice_b = 1 if len(nomes) > 1 else 0
        serie_b = todas[sel_b.selectbox("Série B", nomes, index=indice_b)]
        tipo = transformacoes[
            sel_t.selectbox("Transformação", list(transformacoes))
        ]
        atualizar = botao_atualizar.button("Atualizar dados")

        with st.spinner("Carregando séries..."):
            df_a, _ = carregar_serie(serie_a, atualizar)
            df_b, _ = carregar_serie(serie_b, atualizar)
        if df_a is None or df_b is None:
            st.error("Sem dados: API indisponível e sem cache local.")
            st.stop()

        df_a = _mensalizar(df_a, serie_a)
        df_b = _mensalizar(df_b, serie_b)
        res = correlacionar(df_a[serie_a.slug], df_b[serie_b.slug], tipo)

        c1, c2 = st.columns(2)
        c1.metric("Correlação de Pearson", f"{res['r']:.3f}")
        c2.metric("Observações alinhadas", f"{res['n']}")

        dados = res["dados"]
        fig = px.scatter(
            dados,
            x="a",
            y="b",
            trendline="ols",
            labels={
                "a": f"{serie_a.nome} ({tipo})",
                "b": f"{serie_b.nome} ({tipo})",
            },
            title=f"Correlação — {serie_a.nome} × {serie_b.nome}",
        )
        fig.update_layout(height=480, margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, width="stretch")
        st.markdown(
            """
**Correlação de Pearson:** mede a associação linear entre duas variáveis, de −1 a +1.

- |r| próximo de 1 → forte relação linear; próximo de 0 → relação fraca.
- Correlação ≠ causalidade: duas séries podem andar juntas por um terceiro fator comum.
- Séries não estacionárias em nível tendem a gerar correlação espúria — prefira variação % ou 1ª diferença (use o ADF pra conferir antes).

> **Onde cai no edital:** estatística — correlação, associação linear e correlação espúria.
            """
        )
    else:
        sel_y, sel_x, sel_t, botao_atualizar = st.columns([1, 1, 0.7, 0.5])
        serie_y = todas[sel_y.selectbox("Variável dependente (Y)", nomes)]
        indice_x = 1 if len(nomes) > 1 else 0
        serie_x = todas[
            sel_x.selectbox("Variável explicativa (X)", nomes, index=indice_x)
        ]
        tipo = transformacoes[
            sel_t.selectbox("Transformação", list(transformacoes))
        ]
        atualizar = botao_atualizar.button("Atualizar dados")

        with st.spinner("Carregando séries..."):
            df_x, _ = carregar_serie(serie_x, atualizar)
            df_y, _ = carregar_serie(serie_y, atualizar)
        if df_x is None or df_y is None:
            st.error("Sem dados: API indisponível e sem cache local.")
            st.stop()

        df_x = _mensalizar(df_x, serie_x)
        df_y = _mensalizar(df_y, serie_y)
        res = regressao_simples(df_x[serie_x.slug], df_y[serie_y.slug], tipo)

        tabela = pd.DataFrame(
            [
                {
                    "α (constante)": f"{res['alpha']:.4f}",
                    "β (inclinação)": f"{res['beta']:.4f}",
                    "R²": f"{res['r2']:.3f}",
                    "p-valor de β": f"{res['p_beta']:.4f}",
                    "n": res["n"],
                }
            ]
        )
        st.dataframe(tabela, hide_index=True, width="stretch")

        dados = res["dados"]
        fig = px.scatter(
            dados,
            x="x",
            y="y",
            trendline="ols",
            labels={
                "x": f"{serie_x.nome} ({tipo})",
                "y": f"{serie_y.nome} ({tipo})",
            },
            title=f"Regressão — {serie_y.nome} ~ {serie_x.nome}",
        )
        fig.update_layout(height=480, margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, width="stretch")
        st.markdown(
            """
**Regressão linear simples:** Y = α + βX + ε.

- **β:** variação esperada em Y para cada +1 unidade de X.
- **R²:** fração da variância de Y explicada pelo modelo.
- **p-valor de β:** teste da hipótese H0: β = 0; p < 5% rejeita H0.
- Séries I(1) em nível podem gerar regressão espúria — rode o ADF antes e use variação % ou 1ª diferença.

> **Onde cai no edital:** econometria — MQO, inferência e regressão espúria.
            """
        )


aba_selic, aba_explorador, aba_analises = st.tabs(
    ["SELIC", "Explorador de séries", "Análises"],
    on_change="rerun",
)

if aba_selic.open:
    with aba_selic:
        pagina_selic()

if aba_explorador.open:
    with aba_explorador:
        pagina_explorador()

if aba_analises.open:
    with aba_analises:
        pagina_analises()
