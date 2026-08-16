import pandas as pd
import plotly.express as px
import streamlit as st

from src.bcb import fetch_sgs
from src.catalogo import CATALOGO, Serie
from src.focus import fetch_focus
from src.metrics import acumulada_12m, formatar_periodo, ultima_do_mes
from src.storage import load_series, save_series

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


def pagina_selic() -> None:
    st.title("Dashboard de Séries Macro — BCB/SGS")
    st.caption("Fase 1 — MVP: SELIC mensal (série 4390 da API SGS)")

    @st.cache_data(ttl=3600)
    def baixar_selic() -> pd.DataFrame:
        df = fetch_sgs(SERIE_SELIC_MENSAL, name=NOME_SELIC_MENSAL)
        save_series(df, TABELA_SELIC_MENSAL)
        return df

    @st.cache_data(ttl=3600)
    def baixar_selic_anual() -> pd.DataFrame:
        df = fetch_sgs(SERIE_SELIC_ANUAL, name=NOME_SELIC_ANUAL)
        save_series(df, TABELA_SELIC_ANUAL)
        return df

    @st.cache_data(ttl=3600)
    def baixar_meta() -> pd.DataFrame:
        hoje = pd.Timestamp.today()
        inicio = (hoje - pd.DateOffset(years=10)).strftime("%d/%m/%Y")
        df = fetch_sgs(
            META_SELIC,
            name="meta_selic",
            data_inicial=inicio,
            data_final=hoje.strftime("%d/%m/%Y"),
        )
        save_series(df, TABELA_META)
        return df

    with st.spinner("Buscando SELIC na API SGS..."):
        try:
            df = baixar_selic()
            origem = "API SGS do Banco Central"
        except Exception:
            df = load_series(TABELA_SELIC_MENSAL)
            if df is None:
                st.error("API indisponível e sem cache local. Tente novamente mais tarde.")
                st.stop()
            origem = "cache local (API indisponível)"

    try:
        df_anual = baixar_selic_anual()
    except Exception:
        df_anual = load_series(TABELA_SELIC_ANUAL)

    try:
        meta = baixar_meta()
    except Exception:
        meta = load_series(TABELA_META)

    st.success(
        f"Fonte: {origem} · {len(df)} observações · "
        f"{df.index.min():%b/%Y} a {df.index.max():%b/%Y}"
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


@st.cache_data(ttl=3600, show_spinner=False)
def _baixar_serie(serie: Serie) -> pd.DataFrame:
    if serie.fonte == "focus":
        df = fetch_focus(serie.focus_tipo, name=serie.slug)
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


def carregar_serie(serie: Serie) -> tuple[pd.DataFrame | None, str | None]:
    try:
        return _baixar_serie(serie), "API"
    except Exception:
        df = load_series(serie.slug)
        if df is None:
            return None, None
        return df, "cache local (API indisponível)"


def pagina_explorador() -> None:
    st.title("Explorador de séries")
    st.caption(
        "Fase 2 — blocos: Macroeconomia Aberta, Atividade/PIB, "
        "Política Monetária e Mercado de Capitais"
    )

    blocos = sorted({s.bloco for s in CATALOGO})
    seletor_bloco, seletor_serie = st.columns(2)
    bloco = seletor_bloco.selectbox("Bloco", blocos)
    series_bloco = [s for s in CATALOGO if s.bloco == bloco]
    por_nome = {s.nome: s for s in series_bloco}
    nome = seletor_serie.selectbox("Série", list(por_nome))
    serie = por_nome[nome]

    with st.spinner(f"Buscando {serie.nome}..."):
        df, origem = carregar_serie(serie)

    if df is None:
        st.error("API indisponível e sem cache local. Tente novamente mais tarde.")
        st.stop()

    st.success(
        f"Fonte: {origem} · {len(df)} observações · "
        f"{df.index.min():%b/%Y} a {df.index.max():%b/%Y}"
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


aba_selic, aba_explorador = st.tabs(
    ["SELIC", "Explorador de séries"],
    on_change="rerun",
)

if aba_selic.open:
    with aba_selic:
        pagina_selic()

if aba_explorador.open:
    with aba_explorador:
        pagina_explorador()
