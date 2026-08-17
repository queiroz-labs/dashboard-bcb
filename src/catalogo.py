from dataclasses import dataclass

BLOCO_ABERTA = "Macroeconomia Aberta"
BLOCO_ATIVIDADE = "Atividade e PIB"
BLOCO_POLITICA = "Política Monetária"
BLOCO_MERCADO = "Mercado de Capitais"
BLOCO_EXTERNOS = "Externos"


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
    classificacoes: dict[str, str] | None = None
    focus_tipo: str | None = None
    ticker: str | None = None
    tipo_derivada: str | None = None
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
        slug="desemprego",
        nome="Taxa de desemprego (PNAD Contínua)",
        bloco=BLOCO_ATIVIDADE,
        fonte="sidra",
        agregado="6381",
        variavel="4099",
        frequencia="M",
        unidade="%",
        acumulavel=False,
        contexto="""
**Taxa de desocupação** é o percentual de pessoas desocupadas (sem trabalho e em busca de emprego)
sobre a força de trabalho, medido pela PNAD Contínua do IBGE.

- **Quem publica:** IBGE/PNAD Contínua — agregado 6381, variável 4099 da API SIDRA; mensal.
- **Por que importa:** indica o nível de ociosidade do mercado de trabalho; junto com a inflação,
alimenta a curva de Phillips e a leitura do hiato do produto pelo Copom.
- **Conceitos relacionados:** população em idade de trabalhar, PEA, informalidade, subutilização e
curva de Phillips (desemprego × inflação).
- **Onde cai no edital:** mercado de trabalho e hiato do produto.
        """,
    ),
    Serie(
        slug="rendimento_real",
        nome="Rendimento médio real habitual (PNAD Contínua)",
        bloco=BLOCO_ATIVIDADE,
        fonte="sidra",
        agregado="5436",
        variavel="5933",
        classificacoes={"2": "6794"},
        frequencia="T",
        unidade="R$",
        acumulavel=False,
        contexto="""
**Rendimento médio real habitual** é o valor médio, já descontada a inflação, dos rendimentos de
todos os trabalhos das pessoas ocupadas, segundo a PNAD Contínua.

- **Quem publica:** IBGE/PNAD Contínua — agregado 5436, variável 5934 (total) da API SIDRA; trimestral.
- **Por que importa:** mostra o poder de compra do trabalhador e pressiona a demanda agregada;
crescimento real de salários acima da produtividade tende a gerar pressão inflacionária.
- **Conceitos relacionados:** salário real × nominal, produtividade, massa salarial e inflação de serviços.
- **Onde cai no edital:** mercado de trabalho, renda e inflação.
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
        slug="resultado_primario",
        nome="Resultado primário (12m, % PIB)",
        bloco=BLOCO_POLITICA,
        fonte="sgs",
        codigo_sgs=5793,
        frequencia="M",
        unidade="% PIB (12m)",
        acumulavel=False,
        contexto="""
**Resultado primário** = receitas menos despesas do setor público **excluindo juros** da dívida.
A série é a Necessidade de Financiamento do Setor Público (NFSP) primária, acumulada em 12 meses,
em % do PIB.

- **Quem publica:** Banco Central — série 5793 da API SGS; mensal. **Sinal:** valores positivos
indicam déficit (necessidade de financiamento); negativos, superávit.
- **Por que importa:** é o termômetro da sustentabilidade fiscal. Superávit primário abate a dívida;
déficit recorrente a aumenta, pressionando juros longos e o prêmio de risco.
- **Conceitos relacionados:** resultado nominal × primário, dívida/PIB, regra fiscal e dominância fiscal.
- **Onde cai no edital:** política fiscal e sua interação com a política monetária.
        """,
    ),
    Serie(
        slug="resultado_nominal",
        nome="Resultado nominal (12m, % PIB)",
        bloco=BLOCO_POLITICA,
        fonte="sgs",
        codigo_sgs=5727,
        frequencia="M",
        unidade="% PIB (12m)",
        acumulavel=False,
        contexto="""
**Resultado nominal** = resultado primário **+ juros nominais** incidentes sobre a dívida.
É a variação da dívida líquida no período, em % do PIB (acumulado em 12 meses).

- **Quem publica:** Banco Central — série 5727 da API SGS; mensal. **Sinal:** positivo = déficit
(necessidade de financiamento).
- **Por que importa:** mostra o custo total do endividamento; é a grandeza que determina a trajetória
da dívida quando comparada ao crescimento do PIB.
- **Conceitos relacionados:** juros nominais apropriados, dinâmica da dívida (d = juros − primário),
ajuste patrimonial e desvalorização cambial.
- **Onde cai no edital:** resultado nominal × primário e sustentabilidade da dívida pública.
        """,
    ),
    Serie(
        slug="divida_bruta_pib",
        nome="Dívida bruta do governo geral (% PIB)",
        bloco=BLOCO_POLITICA,
        fonte="sgs",
        codigo_sgs=13762,
        frequencia="M",
        unidade="% PIB",
        acumulavel=False,
        contexto="""
**Dívida Bruta do Governo Geral (DBGG)** abrange o total de débitos de União, estados e municípios
junto ao setor privado, ao setor público financeiro e ao resto do mundo (inclui as compromissadas
do BCB), em % do PIB.

- **Quem publica:** Banco Central — série 13762 da API SGS; mensal (metodologia a partir de 2008).
- **Por que importa:** é a medida de endividamento mais usada em comparações internacionais e pelo
mercado para avaliar o risco fiscal brasileiro.
- **Conceitos relacionados:** dívida bruta × líquida, senhoriagem, teto de gastos e prêmio de risco.
- **Onde cai no edital:** política fiscal — indicadores de dívida pública.
        """,
    ),
    Serie(
        slug="divida_liquida_pib",
        nome="Dívida líquida do setor público (% PIB)",
        bloco=BLOCO_POLITICA,
        fonte="sgs",
        codigo_sgs=4513,
        frequencia="M",
        unidade="% PIB",
        acumulavel=False,
        contexto="""
**Dívida Líquida do Setor Público (DLSP)** é a dívida bruta do setor público consolidado
**descontados os ativos financeiros** (reservas, créditos e aplicações), em % do PIB.

- **Quem publica:** Banco Central — série 4513 da API SGS; mensal.
- **Por que importa:** por ser líquida, reflete melhor a posição patrimonial do setor público e é a
base do resultado nominal (variação da DLSP). Complementa a DBGG na leitura do risco fiscal.
- **Conceitos relacionados:** ativos e passivos do setor público, ajuste patrimonial e senhoriagem.
- **Onde cai no edital:** política fiscal — dívida líquida × bruta do setor público.
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
    Serie(
        slug="credito_pib",
        nome="Saldo de crédito (% PIB)",
        bloco=BLOCO_MERCADO,
        fonte="sgs",
        codigo_sgs=20622,
        frequencia="M",
        unidade="% PIB",
        acumulavel=False,
        contexto="""
**Saldo da carteira de crédito em relação ao PIB** é o estoque de empréstimos do Sistema Financeiro
Nacional dividido pelo PIB acumulado em 12 meses.

- **Quem publica:** Banco Central — série 20622 da API SGS; mensal.
- **Por que importa:** mede a profundidade do mercado de crédito; expansão do crédito financia consumo
e investimento e é um dos canais de transmissão da SELIC para a economia real.
- **Conceitos relacionados:** crédito livre × direcionado, canal de crédito e alavancagem das famílias.
- **Onde cai no edital:** sistema financeiro e transmissão da política monetária.
        """,
    ),
    Serie(
        slug="inadimplencia",
        nome="Inadimplência do crédito (total)",
        bloco=BLOCO_MERCADO,
        fonte="sgs",
        codigo_sgs=21082,
        frequencia="M",
        unidade="%",
        acumulavel=False,
        contexto="""
**Inadimplência** é o percentual da carteira de crédito com ao menos uma parcela em atraso superior
a 90 dias, abrangendo crédito livre e direcionado.

- **Quem publica:** Banco Central — série 21082 da API SGS; mensal.
- **Por que importa:** antecipa perdas dos bancos e aperto de crédito; alta de inadimplência derruba
concessões e esfria a atividade, reforçando o ciclo do juro.
- **Conceitos relacionados:** provisão, spread bancário, risco de crédito e canal de crédito.
- **Onde cai no edital:** mercado de crédito e estabilidade financeira.
        """,
    ),
    Serie(
        slug="concessoes_credito",
        nome="Concessões de crédito (totais)",
        bloco=BLOCO_MERCADO,
        fonte="sgs",
        codigo_sgs=20631,
        frequencia="M",
        unidade="R$ milhões",
        acumulavel=False,
        contexto="""
**Concessões de crédito** são o fluxo de novos empréstimos contratados no mês pelo Sistema
Financeiro Nacional, em R$ milhões.

- **Quem publica:** Banco Central — série 20631 da API SGS; mensal.
- **Por que importa:** é o indicador de fluxo (não de estoque) do crédito; mostra se bancos estão
emprestando mais ou menos, o que antecipa consumo e investimento.
- **Conceitos relacionados:** estoque × fluxo, apetite a risco dos bancos e ciclo de crédito.
- **Onde cai no edital:** mercado de crédito e atividade econômica.
        """,
    ),
    Serie(
        slug="ibovespa",
        nome="Ibovespa (^BVSP)",
        bloco=BLOCO_EXTERNOS,
        fonte="externo",
        ticker="^BVSP",
        frequencia="D",
        unidade="pontos",
        acumulavel=False,
        contexto="""
O **Ibovespa** é o principal índice da B3, composto pelas ações mais negociadas do Brasil.

- **Fonte:** yfinance (ticker ^BVSP) — fonte de protótipo, sem SLA; diária, em pontos.
- **Por que importa:** é o termômetro do mercado acionário brasileiro; oscila com fluxo de capital
estrangeiro, commodities e apetite a risco global.
- **Conceitos relacionados:** risco país, carry trade, prêmio de risco de ações.
- **Onde cai no edital:** mercado de capitais e macroeconomia aberta.
        """,
    ),
    Serie(
        slug="nasdaq",
        nome="Nasdaq Composite (^IXIC)",
        bloco=BLOCO_EXTERNOS,
        fonte="externo",
        ticker="^IXIC",
        frequencia="D",
        unidade="pontos",
        acumulavel=False,
        contexto="""
O **Nasdaq Composite** reúne as ações da bolsa Nasdaq, com forte peso de tecnologia.

- **Fonte:** yfinance (ticker ^IXIC) — fonte de protótipo, sem SLA; diária, em pontos.
- **Por que importa:** é o proxy clássico de apetite a risco global; quedas fortes no Nasdaq
costumam contaminar emergentes e o câmbio brasileiro.
- **Conceitos relacionados:** apetite a risco, contágio e fluxo de capitais.
- **Onde cai no edital:** macroeconomia aberta — transmissão externa.
        """,
    ),
    Serie(
        slug="sp500",
        nome="S&P 500 (^GSPC)",
        bloco=BLOCO_EXTERNOS,
        fonte="externo",
        ticker="^GSPC",
        frequencia="D",
        unidade="pontos",
        acumulavel=False,
        contexto="""
O **S&P 500** é o índice de referência do mercado acionário americano, com as 500 maiores empresas.

- **Fonte:** yfinance (ticker ^GSPC) — fonte de protótipo, sem SLA; diária, em pontos.
- **Por que importa:** é a principal referência global de renda variável; orienta alocação entre
mercados e serve de base de comparação para o risco brasileiro.
- **Conceitos relacionados:** prêmio de risco, diversificação internacional, beta de mercados emergentes.
- **Onde cai no edital:** mercado de capitais e macroeconomia aberta.
        """,
    ),
    Serie(
        slug="usd_jpy",
        nome="USD/JPY (Yen)",
        bloco=BLOCO_EXTERNOS,
        fonte="externo",
        ticker="JPY=X",
        frequencia="D",
        unidade="JPY/USD",
        acumulavel=False,
        contexto="""
O **USD/JPY** mede quantos ienes compram 1 dólar.

- **Fonte:** yfinance (ticker JPY=X) — fonte de protótipo, sem SLA; diária, em JPY/USD.
- **Por que importa:** o iene é a moeda clássica de financiamento do carry trade. Quando o apetite
a risco sobe, investidores tomam ienes emprestados e compram moedas de juro alto (como o real);
quando o risco aperta, o "unwind" valoriza o iene e pressiona emergentes.
- **Conceitos relacionados:** carry trade, paridade descoberta de juros, aversão a risco.
- **Onde cai no edital:** macroeconomia aberta — mercado cambial internacional.
        """,
    ),
    Serie(
        slug="brl_jpy",
        nome="BRL/JPY (Yen em reais)",
        bloco=BLOCO_EXTERNOS,
        fonte="externo",
        tipo_derivada="brl_jpy",
        frequencia="D",
        unidade="BRL/JPY",
        acumulavel=False,
        contexto="""
O **BRL/JPY** é o cruzamento derivado: `BRL/JPY = PTAX (BRL/USD) ÷ USD/JPY (JPY/USD)`.

- **Fonte:** derivado no dashboard a partir da PTAX do BCB e do USD/JPY do yfinance; diária.
- **Por que importa:** mostra o real contra a moeda de funding do carry trade, concentrando em uma
única série o apetite global a risco.
- **Onde cai no edital:** macroeconomia aberta — câmbio cruzado e carry trade.
        """,
    ),
]
