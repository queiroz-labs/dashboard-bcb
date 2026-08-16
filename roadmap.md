# Roadmap — Dashboard de Séries Macro (BCB/SGS)

## Visão geral

Ferramenta de análise e visualização de séries macroeconômicas brasileiras, consumindo dados públicos do Banco Central (API SGS) e fontes complementares (IBGE/SIDRA, IPEA Data). O projeto tem **três objetivos simultâneos**, nessa ordem de prioridade no curto prazo:

1. **Aprendizado de macroeconomia** — fixar conceitos e ler dados reais das áreas cobradas no edital do BACEN (Macroeconomia Aberta, Estatística/Econometria, Finanças e Mercado de Capitais, COSIF).
2. **Prática de programação** — Python aplicado a dados financeiros/macro (APIs, pandas, séries temporais, visualização), evoluindo o nível já alcançado no DRE Forecast.
3. **Comercialização futura** — transformar o projeto em produto vendável depois que a base estiver sólida, reaproveitando a estrutura comercial já resolvida no DRE Forecast (ME Simples Nacional, CNAE 6203-1/00).

Prioridade no dia a dia: **1 e 2 andam juntos desde a Fase 1** (o projeto é literalmente uma forma de estudar fazendo). O objetivo 3 só entra a partir da Fase 4, depois que o produto tiver valor de uso comprovado pra você mesmo.

---

## Stack proposta

| Camada | Escolha | Por quê |
|---|---|---|
| Linguagem | Python | Já em uso, reforça a expansão pra data science |
| Dados | `requests` + API SGS do BCB, SIDRA (IBGE), IPEA Data; `yfinance`/Finnhub como fontes externas de protótipo | Fontes oficiais quando disponíveis; fontes externas ficam isoladas e não são adequadas para produto comercial sem validação |
| Manipulação | pandas | Consolidação do que já usa no DRE Forecast |
| Armazenamento | SQLite (local) → Postgres se for pra SaaS | Simples de começar, migra fácil depois |
| Visualização | Plotly ou Streamlit nativo | Interatividade sem reescrever tudo depois |
| Interface | **Streamlit** (web) — ver decisão em aberto abaixo | Caminho mais rápido pra algo demonstrável e, depois, vendável como SaaS |

**Decisão em aberto:** desktop (CustomTkinter, como o DRE Forecast) vs. web (Streamlit/Dash). Recomendo **web** dessa vez — pra um produto de dados/dashboard, SaaS por assinatura tende a converter melhor que licença desktop, e evita reimplementar a camada de licenciamento Ed25519 que você já resolveu pro DRE Forecast. Mas se quiser manter os dois projetos na mesma linha de distribuição (venda única, offline), desktop também é viável.

**Decisão tomada (ago/2026):** web com **Streamlit** — caminho mais rápido pra algo demonstrável e, depois, vendável como SaaS.

---

## Fase 1 — MVP: primeira série no ar ✅ (concluída em ago/2026)

**Meta:** puxar 1 série (SELIC ou IPCA) da API SGS, salvar localmente, plotar um gráfico de linha simples.

- Programação: autenticação/request HTTP, parsing de JSON, primeiro contato com séries temporais em pandas (`DatetimeIndex`, resample).
- Macro: entender o que a série representa, frequência de divulgação, quem publica, por que importa pra política monetária.
- Entregável: script ou app Streamlit rodando localmente, 1 gráfico funcional.

**Entregue:**
- `app.py` (Streamlit): métricas da SELIC (meta anual do Copom — série 432; taxa efetiva mensal — série 4390; taxa efetiva anualizada base 252 — série 4189; efetiva 12 meses por capitalização composta; máxima pós-Plano Real), gráfico de linha Plotly, seletor de período e card de contexto (o que é, quem publica, por que importa).
- `src/bcb.py`: `fetch_sgs()` — request HTTP + parse JSON → DataFrame com `DatetimeIndex`; aceita `dataInicial`/`dataFinal` (séries diárias têm janela máx. de 10 anos na API).
- `src/storage.py`: cache local em SQLite (`data/bcb.db`) com fallback quando a API está indisponível.
- `src/metrics.py`: `acumulada_12m()` — capitalização composta em janela móvel.
- `tests/test_bcb.py`: 4 testes passing (parse, fetch 4189, fetch 432 com janela, capitalização composta).
- **Correção conceitual (revisão):** o Copom define a meta SELIC **ao ano** (série 432); o SGS oferece a taxa efetiva mensal diretamente na série 4390 (% a.m.) e a série 4189 anualizada em base 252 (% a.a.). O app usa cada série na unidade nativa, sem conversão artificial entre elas. Acumulada em 12 meses = `(1+r1)×…×(1+r12)−1`, não soma. Para taxas efetivas equivalentes, `(1+i a.a.) = (1+i a.m.)^12`.

## Fase 2 — Expansão de indicadores + camada de aprendizado ✅ (concluída em ago/2026)

**Meta:** cobrir um conjunto de ~10-15 séries essenciais, organizadas por bloco temático do edital.

Sugestão de blocos (mapeados ao edital):
- **Macroeconomia Aberta:** câmbio (PTAX), balança comercial, transações correntes, reservas internacionais.
- **Política monetária:** SELIC, IPCA, meta de inflação, expectativas (Focus).
- **Atividade/PIB:** PIB trimestral (IBGE/SIDRA), IBC-Br.
- **Mercado de capitais:** CDI, taxas de juros futuras (se acessível via fonte pública).

Cada série no dashboard ganha um **card de contexto** (o que é, onde cai no edital, fórmula/conceito relacionado) — isso transforma o dashboard num material de estudo, não só numa ferramenta de visualização.

- Programação: modularização (um módulo por fonte de dados), tratamento de séries com frequências diferentes (mensal vs. trimestral vs. diária), primeiros testes automatizados.
- Macro: essa fase é basicamente revisão ativa do bloco de Macroeconomia Aberta e Atividade Econômica do edital.

**Parte A entregue (ago/2026) — blocos Macroeconomia Aberta + Atividade/PIB:**
- `src/catalogo.py`: registro de séries (slug, bloco, fonte, frequência, unidade, card de contexto) — 6 séries: PTAX (1, diária), balança comercial (22701), transações correntes (22702), reservas (3546), IBC-Br (24363), PIB trimestral índice de volume dessaz. (22099).
- `app.py`: abas superiores — SELIC (Fase 1 intacta) e Explorador de séries (bloco → série → métricas, gráfico, card). Séries diárias ganham toggle "agregar mensal (último valor)"; o mecanismo "acumulado 12 meses" já está pronto (reusado na Parte B com IPCA/IGP-M).
- Testes: integridade do catálogo, smoke test parametrizado de todas as séries (15 passing no total).
- **Pendência:** SIDRA/IBGE retornou sem dados no ambiente (".."); PIB veio via SGS (22099).

**Parte B entregue (ago/2026) — Política Monetária:**
- `src/focus.py`: integração filtrada com a API OData Focus, com parser da curva de expectativas do IPCA e da expectativa histórica para uma reunião futura da SELIC.
- `src/catalogo.py`: IPCA mensal (433, acumulável em 12 meses), meta de inflação (13521), expectativa Focus de IPCA e expectativa Focus de SELIC.
- Explorador atualizado para aceitar SGS e Focus, mantendo os cards de contexto e o tratamento de frequências.
- Testes: 22 passing, incluindo parsers Focus e smoke tests das quatro séries novas.

**Parte C entregue (ago/2026) — Mercado de Capitais:**
- CDI diário (SGS 12), explicitamente exibido em `% a.d.` e diário por padrão.
- IGP-M mensal (SGS 189), exibido em `% a.m.` com opção de acumulado composto em 12 meses.
- Catálogo final com 12 séries nos quatro blocos e 25 testes passing.
- Taxas futuras permanecem pendentes até existir uma fonte pública estável definida.

## Fase 3 — Estatística/Econometria aplicada ✅ (concluída em ago/2026)

**Meta:** ir além da visualização — adicionar análises que praticam o bloco de Estatística/Econometria do edital.

- Decomposição de séries (tendência, sazonalidade, ciclo).
- Correlação entre indicadores (ex: câmbio x IPCA, SELIC x IBC-Br).
- Regressões simples (ex: Focus vs. IPCA realizado — erro de previsão do mercado).
- Testes de estacionariedade (ADF) — direto do syllabus de econometria.

- Programação: `statsmodels`, primeiros modelos, visualização de resultados estatísticos.
- Macro/Estatística: essa fase é a mais alinhada ao bloco mais técnico da prova — o dashboard vira literalmente um caderno de exercícios interativo.

**Entregue (ago/2026):**
- Nova aba "Análises" com **Decomposição** (tendência/sazonal/resíduo, aditiva, period=12), **Teste ADF** (nível + 1ª diferença, com p-valor, críticos e conclusão), **Correlação** (Pearson, com transformações nível/variação %/1ª diferença) e **Regressão simples** (α, β, R², p-valor e gráfico OLS).
- `src/econometria.py`: `decompor()`, `rodar_adf()`, `transformar()`, `correlacionar()` e `regressao_simples()` com statsmodels.
- Séries diárias são mensalizadas automaticamente nas análises (último valor do mês).
- Cards de interpretação estatística conectados ao edital (raiz unitária, ordem de integração, correlação espúria, MQO).
- **Cache sob demanda implementado (pendência resolvida):** o app lê primeiro do SQLite e só consulta a API quando o usuário clica em "Atualizar dados" (ou quando não há cache); cada série exibe a "última atualização" (`src/storage.py: salvar_meta/ler_meta`).
- Testes: 39 passing (econometria sintética, metadados de cache, parsers), 5 skips de fontes externas no smoke test.

## Expansão 3B — Dados externos e correlação global ✅ (concluída em ago/2026)

Esta expansão complementa a Fase 3 sem reabrir a Fase 2. O objetivo é permitir a leitura de relações entre Brasil e mercados globais, especialmente no bloco de Macroeconomia Aberta.

**Indicadores:**
- Ibovespa (`^BVSP`), Nasdaq (`^IXIC`) e S&P 500 (`^GSPC`), via `yfinance`.
- USD/JPY via `yfinance` (`JPY=X`), cruzado com a PTAX do BCB para derivar BRL/JPY: `BRL/JPY = PTAX (BRL/USD) ÷ USD/JPY (JPY/USD)`.

**Mudanças técnicas:**
- `src/externos.py`: `fetch_ticker()` (coluna Close, índice diário sem timezone) e `cruzamento_brl_jpy()` (função pura).
- Catálogo estendido com bloco **Externos** e campos `ticker`/`tipo_derivada`; cards de contexto (apetite a risco, carry trade).
- Cache reutilizado (`_buscar_ou_cache` + `meta_series`); `.env` adicionado ao `.gitignore`.
- `yfinance` instalado e pinado no `requirements.txt` (1.6.0) — fonte de protótipo, sem SLA.
- Testes com yfinance mockado (parse, multi-índice, cruzamento).

**Aplicação econométrica (validada com dados reais):**
- Correlação mensal (variação %) Ibovespa × PTAX ≈ −0,69; S&P 500 × PTAX ≈ −0,34.
- Regressão PTAX ~ S&P 500 (variação %): β ≈ −0,30, R² ≈ 0,11, p-valor < 0,001.

**Critério de conclusão atingido:** 5 séries externas no Explorador (3 índices + USD/JPY + BRL/JPY derivado), com cache local, unidades documentadas, fallback via cache e nenhuma chave exposta. Finnhub segue reservado para a agenda econômica na Fase 4.

## Fase 4 — Produto: UX e diferenciação

**Meta:** sair de "ferramenta pessoal de estudo" para algo que outra pessoa pagaria por usar.

- Público-alvo a definir: candidatos a concursos de área econômica (BACEN, ANPEC, outros)? Analistas financeiros júnior? Pequenas empresas que precisam de contexto macro pro planejamento (conecta com o público do DRE Forecast)?
- UX: exportação de relatórios (PDF/Excel), alertas de mudança de indicador, comparação histórica (ex: "SELIC hoje vs. mesmo período em crises passadas").
- UX adicional: agenda econômica semanal com decisões de juros, PIB, payroll, CPI e outros eventos relevantes, exibindo data/hora, país, anterior, expectativa, realizado e impacto.
- Programação: polish de interface, performance de carregamento e evolução do cache de dados da API.
- Agenda: padronizar datas para o fuso `America/Sao_Paulo`, tratar horário de verão quando aplicável e normalizar diferenças entre fontes.

## Fase 5 — Comercialização

**Meta:** validar e lançar.

- Definir modelo: assinatura mensal (SaaS) vs. relatório avulso vs. bundle com o DRE Forecast (mesma base de clientes B2B/controllers?).
- Reaproveitar estrutura já resolvida: ME Simples Nacional, CNAE 6203-1/00 já cobre esse tipo de atividade — não deve exigir nova estrutura jurídica.
- Canais: mesmo playbook já mapeado pro DRE Forecast (LinkedIn outbound, parcerias) ou público diferente (concurseiros — comunidades, grupos de estudo, cursinhos como o Curso Macetes)?
- Pricing: pesquisar disposição a pagar nos dois públicos antes de decidir.

---

## Riscos e decisões em aberto

- **Desktop vs. web** ✅ resolvido — Streamlit web (ver Fase 1).
- **Dependência de APIs públicas:** SGS do BCB é estável e o cache SQLite já mitiga indisponibilidade; `yfinance` não tem SLA (fica restrito a protótipo até a Fase 5) e o Finnhub, se usado na agenda (Fase 4), exige chave e respeita limite de chamadas.
- **Segredos e configuração externa:** `.env` já está fora do Git; se o Finnhub entrar, a chave vai em variável de ambiente, nunca versionada.
- **Fuso horário da agenda:** eventos externos podem vir em UTC ou horário de Nova York; toda exibição deve ser convertida para `America/Sao_Paulo`.
- **Escopo de aprendizado vs. escopo de produto:** garantir que features "de estudo" (cards de contexto, explicações) não fiquem em conflito com o que um comprador não-concurseiro quer ver.
- **Timing:** BACEN é prioridade máxima até o edital sair (~jan/2027). Esse projeto deve reforçar o estudo, não competir com ele — se em algum momento virar distração, phases 4-5 esperam.

---

## Métricas de sucesso por fase

| Fase | Como saber que deu certo |
|---|---|
| 1 | App roda local, 1 gráfico correto |
| 2 | 10+ séries no ar, você consegue "estudar" usando o próprio dashboard |
| 3 | Consegue responder questões de estatística/econometria do edital usando dados reais do projeto |
| 3B | 4+ indicadores externos integrados, cacheados e usados em uma correlação Brasil × exterior |
| 4 | Alguém fora de você usaria sem precisar de explicação |
| 5 | Primeira venda ou primeira assinatura paga |
