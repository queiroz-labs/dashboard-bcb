from dataclasses import dataclass

BLOCO_ABERTA = "Macroeconomia Aberta"
BLOCO_ATIVIDADE = "Atividade e PIB"


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
]
