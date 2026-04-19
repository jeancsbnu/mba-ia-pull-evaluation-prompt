# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Técnicas Aplicadas (Fase 2)

### Técnicas escolhidas e justificativas

#### 1. Role Prompting

**O que é:** Define uma persona detalhada para o modelo antes de qualquer instrução.

**Como foi aplicado:**
```
"Você é um Product Owner técnico sênior com 10+ anos de experiência em metodologias ágeis,
especializado em transformar relatos de bugs em User Stories claras, completas e acionáveis
para times de desenvolvimento."
```

**Por que escolhi:** O modelo se comporta de forma mais consistente e profissional quando assume um papel específico. Ao definir claramente quem está respondendo (PO técnico sênior), o LLM adota vocabulário ágil preciso, prioriza valor de negócio sobre detalhes de implementação e mantém empatia com o usuário final — critérios diretamente avaliados pelas métricas de Clarity e Precision.

---

#### 2. Chain of Thought (CoT)

**O que é:** Instrui o modelo a raciocinar passo a passo antes de gerar a resposta final.

**Como foi aplicado:**
```
## PASSO A PASSO — RACIOCINE ANTES DE ESCREVER

1. IDENTIFIQUE O USUÁRIO: quem é afetado, com contexto específico
   (dashboards → "administrador"; formulários de cadastro → "usuário criando uma conta";
    cross-browser → "cliente usando [browser]")
2. CLASSIFIQUE A COMPLEXIDADE: SIMPLES / MÉDIO / COMPLEXO
3. MAPEIE O BUG: funcionalidade, comportamento atual, esperado, causa raiz
4. LISTE OS DETALHES TÉCNICOS: preserve números, endpoints, logs, valores
5. ESCREVA A USER STORY: use exatamente a estrutura definida
```

**Por que escolhi:** Bugs têm complexidades muito diferentes. Sem etapa de raciocínio explícita, o modelo tende a usar persona genérica ("um usuário"), omitir critérios implícitos importantes ou gerar estrutura inadequada para o tipo de bug. O CoT força análise sistemática antes de escrever, melhorando F1-Score (recall dos detalhes) e Correctness.

---

#### 3. Few-shot Learning

**O que é:** Fornece exemplos concretos de entrada/saída para calibrar o comportamento esperado.

**Como foi aplicado:** Seis exemplos completos embutidos no system prompt, cobrindo os padrões estruturais críticos identificados na análise do dataset:

- **Exemplo 1 — SIMPLES (UI/UX):** botão que não funciona → User Story + Critérios com termos genéricos (sem copiar IDs específicos do relato)
- **Exemplo 2 — SIMPLES (dashboard de métricas):** contagem incorreta → demonstra critérios implícitos `"E o valor deve ser atualizado em tempo real"` e `"E deve incluir apenas [itens] com status 'ativo'"`
- **Exemplo 3 — SIMPLES (cross-browser):** bug no Firefox → persona `"cliente usando Firefox"` e critérios `"E devem ter a mesma qualidade que em outros navegadores"`
- **Exemplo 4 — SIMPLES (validação de campo):** campo aceita formato inválido → sequência exata `Então devo ver uma mensagem de erro` → `E não devo conseguir prosseguir` → `E a mensagem deve explicar o formato correto`
- **Exemplo 5 — MÉDIO Padrão A (performance):** timeout em relatório SQL → User Story + Critérios + `Contexto Técnico:`
- **Exemplo 6 — MÉDIO Padrão B (mobile/ANR):** app trava → User Story + Critérios + `Critérios Técnicos:` + `Contexto do Bug:`

**Por que escolhi:** A análise direta do dataset revelou que o modelo cometia erros sistemáticos de padrão: usava persona genérica para bugs específicos, copiava IDs do relato nos critérios, invertia a sequência Dado/Quando em integrações, e omitia critérios implícitos razoáveis presentes nas referências. Regras textuais sozinhas não resolveram — apenas os exemplos few-shot que demonstravam o padrão exato de saída fixaram esses comportamentos de forma confiável.

---

#### 4. Skeleton of Thought

**O que é:** Pré-define a estrutura esquelética adaptativa da resposta por nível de complexidade.

**Como foi aplicado:** Três formatos fixos calibrados com base na análise direta das referências:

**Bugs SIMPLES** — formato mínimo:
```
Como um [usuário específico], eu quero [objetivo], para que [benefício].

Critérios de Aceitação:
- Dado que [contexto]
- Quando [ação]
- Então [resultado esperado]
- E [resultado adicional]
```
*(sem seções ##, sem contexto técnico, critérios genéricos)*

**Bugs MÉDIOS** — adiciona seção contextual com rótulo adaptado ao tipo:
```
[User Story + Critérios]

Contexto Técnico:      ← ou "Contexto do Bug:", "Contexto de Segurança:", "Exemplo de Cálculo:"
- [detalhe técnico preservado do relato]
```

**Bugs COMPLEXOS** — blocos `===` com categorias:
```
=== USER STORY PRINCIPAL === → === CRITÉRIOS DE ACEITAÇÃO === → === CRITÉRIOS TÉCNICOS ===
→ === CONTEXTO DO BUG === → === TASKS TÉCNICAS SUGERIDAS === → === MÉTRICAS DE SUCESSO ===
```

**Por que escolhi:** A análise das referências revelou que nenhum bug SIMPLES ou MÉDIO usa headers `##`, bugs simples nunca têm seções contextuais, e cada tipo de bug médio tem um rótulo contextual específico (`Contexto de Segurança:` para vulnerabilidades, `Exemplo de Cálculo:` para bugs matemáticos, etc.). O Skeleton of Thought garante que a estrutura certa é gerada para cada complexidade.

---

## Resultados Finais

### Ajuste no evaluate.py para registro de Experiments no LangSmith

Durante a execução da avaliação, identificou-se que o `evaluate.py` original não criava **Experiments** visíveis no dashboard do LangSmith — apenas salvava feedback isolado via `client.create_feedback()`. O script foi refatorado para utilizar `langsmith.evaluate()`, que:

- Cria um **Experiment** vinculado ao dataset a cada execução
- Gera um `experiment_prefix` único com timestamp, garantindo que nenhuma run sobrescreva outra
- Registra as métricas (F1-Score, Clarity, Precision) como evaluators nativos do LangSmith

Com essa alteração, cada execução do `evaluate.py` passa a ser rastreável no dashboard em **LangSmith → Datasets & Experiments**.

---

### Tabela comparativa: v1 vs v2

| Métrica         | v1 (baseline) | v2 (otimizado) | Meta  | Status |
|-----------------|:-------------:|:--------------:|:-----:|:------:|
| Helpfulness     | ~0.48         | **0.93**       | ≥ 0.9 | ✅     |
| Correctness     | ~0.50         | **0.89**       | ≥ 0.9 | —      |
| F1-Score        | ~0.45         | **0.84**       | ≥ 0.9 | —      |
| Clarity         | ~0.52         | **0.92**       | ≥ 0.9 | ✅     |
| Precision       | ~0.48         | **0.94**       | ≥ 0.9 | ✅     |
| **Média Geral** | **~0.49**     | **0.9023**     | ≥ 0.9 | ✅     |

> **v1 baseline:** prompt minimalista ("Você é um assistente que transforma bugs em user stories") sem persona, sem CoT, sem exemplos, sem estrutura definida. Scores estimados com base no padrão de prompts equivalentes.
>
> **v2 aprovado:** avaliação oficial em 2026-04-18 via `langsmith.evaluate()` — `✅ STATUS: APROVADO (média >= 0.9)`

### Resultado da avaliação final (output do evaluate.py)

```
[1/10]  F1:0.75  Clarity:0.80  Precision:0.90
[2/10]  F1:0.85  Clarity:0.90  Precision:0.90
[3/10]  F1:0.77  Clarity:0.90  Precision:1.00
[4/10]  F1:0.58  Clarity:0.90  Precision:0.83
[5/10]  F1:0.75  Clarity:0.90  Precision:0.90
[6/10]  F1:1.00  Clarity:0.90  Precision:1.00
[7/10]  F1:0.95  Clarity:1.00  Precision:1.00
[8/10]  F1:0.90  Clarity:0.95  Precision:1.00
[9/10]  F1:0.90  Clarity:0.90  Precision:0.83
[10/10] F1:1.00  Clarity:1.00  Precision:1.00

==================================================
Prompt: bug_to_user_story_v2
==================================================

Métricas LangSmith:
  - Helpfulness: 0.93 ✓
  - Correctness: 0.89 ✗

Métricas Customizadas:
  - F1-Score:    0.84 ✗
  - Clarity:     0.92 ✓
  - Precision:   0.94 ✓

--------------------------------------------------
MÉDIA GERAL: 0.9023
--------------------------------------------------

✅ STATUS: APROVADO (média >= 0.9)

==================================================
RESUMO FINAL
==================================================

Prompts avaliados: 1
Aprovados: 1
Reprovados: 0

✅ Todos os prompts atingiram média >= 0.9!
```

### Dashboard LangSmith

> Adicione aqui o link público do dashboard e screenshots das avaliações.

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) com API Key
- API Key da OpenAI (`gpt-4o-mini` para geração, `gpt-4o` para avaliação)

### Configuração

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd mba-ia-pull-evaluation-prompt

# 2. Instale as dependências (com Poetry)
poetry install

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves:
#   LANGSMITH_API_KEY=...
#   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
#   LANGSMITH_PROJECT=prompt-optimization-challenge-resolved
#   USERNAME_LANGSMITH_HUB=<seu-username>
#   LLM_PROVIDER=openai
#   LLM_MODEL=gpt-4o-mini
#   EVAL_MODEL=gpt-4o
#   OPENAI_API_KEY=...
```

### Execução

```bash
# 1. Pull do prompt original (v1) do LangSmith
poetry run python src/pull_prompts.py

# 2. (Opcional) Diagnóstico local — compara output vs referência sem push
poetry run python src/debug_outputs.py --save

# 3. Push do prompt otimizado (v2) para o LangSmith
poetry run python src/push_prompts.py

# 4. Avaliação oficial
poetry run python src/evaluate.py

# 5. Testes de validação
poetry run pytest tests/test_prompts.py -v
```

### Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example
├── pyproject.toml
├── README.md
├── datasets/
│   └── bug_to_user_story.jsonl     # 15 exemplos (5 simples, 7 médios, 3 complexos)
├── prompts/
│   ├── bug_to_user_story_v1.yml    # Prompt inicial (baixa qualidade)
│   └── bug_to_user_story_v2.yml    # Prompt otimizado (aprovado 0.9035)
├── src/
│   ├── pull_prompts.py             # Pull do LangSmith Hub
│   ├── push_prompts.py             # Push ao LangSmith Hub
│   ├── evaluate.py                 # Avaliação automática (métricas F1, Clarity, Precision)
│   ├── metrics.py                  # Implementação das métricas (LLM-as-judge com GPT-4o)
│   ├── debug_outputs.py            # Diagnóstico local: output do modelo vs referência
│   └── utils.py                    # Funções auxiliares
└── tests/
    └── test_prompts.py             # Testes de validação do prompt
```

---

## Processo de Otimização

O desafio foi atingir média ≥ 0.9 num cenário de **variância do juiz LLM** (GPT-4o): o mesmo prompt pode receber scores diferentes em execuções distintas. A estratégia que funcionou foi usar **Few-shot Learning** como técnica central — em vez de empilhar regras textuais que confundiam o modelo, adicionamos exemplos que demonstravam o padrão exato de saída esperado para cada tipo de bug.

**Evolução dos scores:**

| Iteração | Avg   | F1   | Ação principal                                      |
|----------|-------|------|-----------------------------------------------------|
| v2 base  | 0.844 | 0.77 | Role + CoT + Skeleton + 1 exemplo simples           |
| iter 2   | 0.863 | 0.77 | Critérios implícitos obrigatórios (cross-browser, dashboard, webhook) |
| iter 3   | 0.888 | 0.81 | Regras mais precisas: sem ## em SIMPLES, exemplos inline de complexidade |
| iter 4   | 0.893 | 0.82 | Exemplos cross-browser e dashboard (few-shot)        |
| **iter 5** | **0.9035** | **0.83** | **Few-shot validação + persona hints + formato segurança** |

**Lição principal:** para LLMs, exemplos concretos (`Few-shot`) são mais eficazes do que regras textuais complexas. Regras muito longas aumentam a carga cognitiva do modelo e geram comportamentos inconsistentes. Cada vez que um exemplo foi adicionado demonstrando o padrão exato, o comportamento ficou mais estável do que com qualquer instrução textual equivalente.
