from dataclasses import dataclass

BLOCO_ABERTA = "Macroeconomia Aberta"
BLOCO_ATIVIDADE = "Atividade e PIB"
BLOCO_POLITICA = "Política Monetária"
BLOCO_MERCADO = "Mercado de Capitais"


@dataclass(frozen=True)
class Serie:
    slug: str
    nome: str
    bloco: str
    fonte: str
    frequencia: str
    unidade: str
    contexto: str
    codigo_sgs: int | None = None
    agregado: str | None = None
    variavel: str | None = None
    focus_tipo: str | None = None
    acumulavel: bool = False


CATALOGO: list[Serie] = [
    Serie(
        slug="ptax",
        nome="PTAX (dólar comercial)",
        bloco=BLOCO_ABERTA,
        fonte="sgs",
        codigo_sgs=1,
        frequencia="D",
        unidade="R$/US$",
        acumulavel=False,
        contexto="""
**PTAX** é a **taxa de câmbio de referência** divulgada pelo Banco Central: a cotação do dólar
americano (venda) calculada a partir das operações do mercado interbancário.

- **Quem publica:** Banco Central — série 1 da API SGS, frequência diária, unidade R$/US$.
- **Por que importa:** é a taxa usada em contratos, impostos de importação/exportação, balanços
e derivativos. Movimentos da PTAX refletem oferta/demanda de moeda estrangeira, política monetária
do BCB e do Fed, e risco-país.
- **Conceitos relacionados:** câmbio nominal × real, regimes cambiais (flutuante sujo no Brasil),
paridade de juros (Selic × Fed).
- **Onde cai no edital:** macroeconomia aberta — mercado cambial e regimes de câmbio.
        """,
    ),
    Serie(
        slug="balanca_comercial",
        nome="Balança comercial",
        bloco=BLOCO_ABERTA,
        fonte="sgs",
        codigo_sgs=22701,
        frequencia="M",
        unidade="US$ milhões",
        acumulavel=False,
        contexto="""
**Balança comercial** = exportações − importações (FOB). Superávit quando o país exporta mais
do que importa.

- **Quem publica:** Banco Central — série 22701 da API SGS; mensal, US$ milhões.
- **Por que importa:** é o principal componente das transações correntes; superávits persistentes
indicam competitividade externa e ajudam a acumular reservas.
- **Conceitos relacionados:** termos de troca, commodities, câmbio como determinante do saldo.
- **Onde cai no edital:** balanço de pagamentos — balança comercial.
        """,
    ),
    Serie(
        slug="transacoes_correntes",
        nome="Transações correntes",
        bloco=BLOCO_ABERTA,
        fonte="sgs",
        codigo_sgs=22702,
        frequencia="M",
        unidade="US$ milhões",
        acumulavel=False,
        contexto="""
**Transações correntes** = balança comercial + serviços + renda primária (juros, lucros e dividendos)
+ renda secundária (transferências). Mede se o país "gasta mais do que ganha" com o exterior.

- **Quem publica:** Banco Central — série 22702 da API SGS; mensal, US$ milhões.
- **Por que importa:** déficit persistente exige financiamento externo (investimentos/empréstimos);
a relação com a conta financeira é a identidade do balanço de pagamentos.
- **Conceitos relacionados:** identidade BP = conta corrente + conta capital + conta financeira = 0;
posição internacional de investimentos.
- **Onde cai no edital:** balanço de pagamentos.
        """,
    ),
    Serie(
        slug="reservas_internacionais",
        nome="Reservas internacionais",
        bloco=BLOCO_ABERTA,
        fonte="sgs",
        codigo_sgs=3546,
        frequencia="M",
        unidade="US$ milhões",
        acumulavel=False,
        contexto="""
**Reservas internacionais** são os ativos em moeda estrangeira do Banco Central (títulos, ouro,
direitos especiais de saque), usados pra intervir no câmbio e honrar compromissos externos.

- **Quem publica:** Banco Central — série 3546 da API SGS; mensal, US$ milhões.
- **Por que importa:** funcionam como colchão contra crises cambiais ("sudden stops"); países
emergentes mantêm reservas altas como autosseguro.
- **Conceitos relacionados:** custo de carregamento das reservas, intervenção cambial, rating soberano.
- **Onde cai no edital:** macroeconomia aberta — crise cambial e política de reservas.
        """,
    ),
    Serie(
        slug="ibc_br",
        nome="IBC-Br (atividade econômica)",
        bloco=BLOCO_ATIVIDADE,
        fonte="sgs",
        codigo_sgs=24363,
        frequencia="M",
        unidade="índice (dessaz.)",
        acumulavel=False,
        contexto="""
**IBC-Br** (Índice de Atividade Econômica do Banco Central) é um indicador **mensal** que antecipa
o PIB trimestral, construído a partir de proxies de agropecuária, indústria e serviços.

- **Quem publica:** Banco Central — série 24363 da API SGS (índice dessazonalizado); mensal.
- **Por que importa:** é a melhor leitura mensal do ritmo da atividade; o mercado usa pra projetar
o PIB antes do IBGE divulgar.
- **Conceitos relacionados:** dessazonalização, índice de volume, PIB × IBC-Br.
- **Onde cai no edital:** contas nacionais / atividade econômica.
        """,
    ),
    Serie(
        slug="pib_volume",
        nome="PIB trimestral (índice de volume dessaz.)",
        bloco=BLOCO_ATIVIDADE,
        fonte="sgs",
        codigo_sgs=22099,
        frequencia="T",
        unidade="índice (1995=100)",
        acumulavel=False,
        contexto="""
**PIB trimestral** — índice encadeado de volume com ajuste sazonal, base 1995 = 100
(Contas Nacionais Trimestrais, republicado pelo Banco Central).

- **Quem publica:** IBGE (Contas Nacionais Trimestrais); série 22099 da API SGS do BCB; trimestral.
- **Por que importa:** é a medida oficial do crescimento econômico; acelerações/desacelerações
guiam decisões de política monetária e fiscal.
- **Conceitos relacionados:** PIB pelas óticas da despesa/renda/produção, crescimento real × nominal,
dessazonalização (ajuste sazonal), deflator implícito.
- **Onde cai no edital:** contas nacionais — PIB e componentes.
        """,
    ),
    Serie(
        slug="ipca",
        nome="IPCA mensal",
        bloco=BLOCO_POLITICA,
        fonte="sgs",
        codigo_sgs=433,
        frequencia="M",
        unidade="% a.m.",
        acumulavel=True,
        contexto="""
**IPCA** (Índice Nacional de Preços ao Consumidor Amplo) é o índice oficial de inflação do Brasil,
calculado pelo IBGE a partir de uma cesta de bens e serviços consumidos pelas famílias.

- **Quem publica:** IBGE; série 433 da API SGS do Banco Central; variação mensal em % a.m.
- **Por que importa:** é a referência do regime de metas de inflação e orienta decisões do Copom.
- **Conceitos relacionados:** índice de preços, inflação cheia e núcleos, inflação acumulada e
efeito de segunda ordem.
- **Onde cai no edital:** inflação, índices de preços e política monetária.
        """,
    ),
    Serie(
        slug="meta_ipca",
        nome="Meta de inflação (IPCA)",
        bloco=BLOCO_POLITICA,
        fonte="sgs",
        codigo_sgs=13521,
        frequencia="A",
        unidade="% a.a.",
        acumulavel=False,
        contexto="""
**A meta de inflação** é o objetivo anual para a variação do IPCA dentro do regime brasileiro
de metas, definido pelo Conselho Monetário Nacional.

- **Quem define:** CMN; série 13521 da API SGS; uma observação por ano, em % a.a.
- **Por que importa:** ancora expectativas e dá ao Banco Central o objetivo contra o qual a inflação
realizada e a política monetária são avaliadas.
- **Conceitos relacionados:** intervalo de tolerância, expectativas racionais, credibilidade e
custo da desinflação.
- **Onde cai no edital:** regime de metas de inflação e instituições do Sistema Financeiro Nacional.
        """,
    ),
    Serie(
        slug="focus_ipca",
        nome="Expectativa Focus — IPCA mensal",
        bloco=BLOCO_POLITICA,
        fonte="focus",
        focus_tipo="ipca",
        frequencia="M",
        unidade="% esperado",
        acumulavel=False,
        contexto="""
**A pesquisa Focus** reúne projeções do mercado para indicadores macroeconômicos. Esta série mostra
as medianas mais recentes das expectativas para o IPCA de cada mês futuro.

- **Quem publica:** Banco Central, pesquisa de expectativas via API Olinda; atualização semanal.
- **Por que importa:** expectativas de inflação afetam preços, salários, contratos e a decisão do Copom.
- **Conceitos relacionados:** formação de expectativas, curva de Phillips e ancoragem das expectativas.
- **Onde cai no edital:** política monetária, inflação esperada e mecanismo de transmissão.
        """,
    ),
    Serie(
        slug="focus_selic",
        nome="Expectativa Focus — SELIC",
        bloco=BLOCO_POLITICA,
        fonte="focus",
        focus_tipo="selic",
        frequencia="D",
        unidade="% a.a. esperado",
        acumulavel=False,
        contexto="""
Esta série acompanha a mediana das expectativas do mercado para a SELIC em uma reunião futura
do Copom, ao longo das datas de divulgação da pesquisa Focus.

- **Quem publica:** Banco Central, pesquisa de expectativas via API Olinda; atualização semanal.
- **Por que importa:** resume a trajetória esperada dos juros e ajuda a interpretar a curva de juros.
- **Conceitos relacionados:** juros nominais e reais, prêmio de risco, forward guidance e curva a termo.
- **Onde cai no edital:** política monetária e mercado de renda fixa.
        """,
    ),
    Serie(
        slug="cdi",
        nome="CDI diário",
        bloco=BLOCO_MERCADO,
        fonte="sgs",
        codigo_sgs=12,
        frequencia="D",
        unidade="% a.d.",
        acumulavel=False,
        contexto="""
O **CDI** é a taxa de referência das operações de empréstimo de um dia entre instituições financeiras.
A série mostra a taxa diária, em percentual ao dia.

- **Quem publica:** Banco Central; série 12 da API SGS; frequência diária, unidade % a.d.
- **Por que importa:** serve como referência para aplicações de renda fixa e costuma acompanhar de perto
a SELIC efetiva.
- **Conceitos relacionados:** mercado interfinanceiro, operações compromissadas, taxa over e liquidez.
- **Onde cai no edital:** mercado monetário, formação da taxa de juros e mercado de capitais.

> **Atenção à unidade:** o valor exibido é diário (% a.d.), não anualizado (% a.a.) nem mensal (% a.m.).
        """,
    ),
    Serie(
        slug="igpm",
        nome="IGP-M mensal",
        bloco=BLOCO_MERCADO,
        fonte="sgs",
        codigo_sgs=189,
        frequencia="M",
        unidade="% a.m.",
        acumulavel=True,
        contexto="""
O **IGP-M** (Índice Geral de Preços — Mercado) mede a variação de preços no atacado, no consumidor

- **Quem publica:** Fundação Getulio Vargas; série 189 da API SGS; variação mensal em % a.m.
- **Por que importa:** é usado como indexador de contratos e ajuda a acompanhar pressões de preços
que podem diferir da cesta do IPCA.
- **Conceitos relacionados:** inflação ao produtor, indexação, inércia inflacionária e composição de índices.
- **Onde cai no edital:** índices de preços, inflação e contratos financeiros.

> **Atenção à unidade:** o valor bruto é mensal (% a.m.); o toggle de acumulado usa capitalização
composta dos últimos 12 meses.
        """,
    ),
]
