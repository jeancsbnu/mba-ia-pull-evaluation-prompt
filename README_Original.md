# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Exemplo no CLI

```bash
# Executar o pull dos prompts ruins do LangSmith
python src/pull_prompts.py

# Executar avaliação inicial (prompts ruins)
python src/evaluate.py

Executando avaliação dos prompts...
================================
Prompt: support_bot_v1a
- Helpfulness: 0.45
- Correctness: 0.52
- F1-Score: 0.48
- Clarity: 0.50
- Precision: 0.46
================================
Status: FALHOU - Métricas abaixo do mínimo de 0.9

# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação final (prompts otimizados)
python src/evaluate.py

Executando avaliação dos prompts...
================================
Prompt: support_bot_v2_optimized
- Helpfulness: 0.94
- Correctness: 0.96
- F1-Score: 0.93
- Clarity: 0.95
- Precision: 0.92
================================
Status: APROVADO ✓ - Todas as métricas atingiram o mínimo de 0.9
```
---

## Tecnologias obrigatórias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

- Crie uma **API Key** da OpenAI: https://platform.openai.com/api-keys
- **Modelo de LLM para responder**: `gpt-4o-mini`
- **Modelo de LLM para avaliação**: `gpt-4o`
- **Custo estimado:** ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma **API Key** da Google: https://aistudio.google.com/app/apikey
- **Modelo de LLM para responder**: `gemini-2.5-flash`
- **Modelo de LLM para avaliação**: `gemini-2.5-flash`
- **Limite:** 15 req/min, 1500 req/dia

---

## Requisitos

### 1. Pull dos Prompt inicial do LangSmith

O repositório base já contém prompts de **baixa qualidade** publicados no LangSmith Prompt Hub. Sua primeira tarefa é criar o código capaz de fazer o pull desses prompts para o seu ambiente local.

**Tarefas:**

1. Configurar suas credenciais do LangSmith no arquivo `.env` (conforme instruções no `README.md` do repositório base)
2. Acessar o script `src/pull_prompts.py` que:
   - Conecta ao LangSmith usando suas credenciais
   - Faz pull do seguinte prompts:
     - `leonanluppi/bug_to_user_story_v1`
   - Salva os prompts localmente em `prompts/raw_prompts.yml`

---

### 2. Otimização do Prompt

Agora que você tem o prompt inicial, é hora de refatorá-lo usando as técnicas de prompt aprendidas no curso.

**Tarefas:**

1. Analisar o prompt em `prompts/bug_to_user_story_v1.yml`
2. Criar um novo arquivo `prompts/bug_to_user_story_v2.yml` com suas versões otimizadas
3. Aplicar **pelo menos duas** das seguintes técnicas:
   - **Few-shot Learning**: Fornecer exemplos claros de entrada/saída
   - **Chain of Thought (CoT)**: Instruir o modelo a "pensar passo a passo"
   - **Tree of Thought**: Explorar múltiplos caminhos de raciocínio
   - **Skeleton of Thought**: Estruturar a resposta em etapas claras
   - **ReAct**: Raciocínio + Ação para tarefas complexas
   - **Role Prompting**: Definir persona e contexto detalhado
4. Documentar no `README.md` quais técnicas você escolheu e por quê

**Requisitos do prompt otimizado:**

- Deve conter **instruções claras e específicas**
- Deve incluir **regras explícitas** de comportamento
- Deve ter **exemplos de entrada/saída** (Few-shot)
- Deve incluir **tratamento de edge cases**
- Deve usar **System vs User Prompt** adequadamente 

---

### 3. Push e Avaliação

Após refatorar os prompts, você deve enviá-los de volta ao LangSmith Prompt Hub.

**Tarefas:**

1. Criar o script `src/push_prompts.py` que:
   - Lê os prompts otimizados de `prompts/bug_to_user_story_v2.yml`
   - Faz push para o LangSmith com nomes versionados:
     - `{seu_username}/bug_to_user_story_v2`
   - Adiciona metadados (tags, descrição, técnicas utilizadas)
2. Executar o script e verificar no dashboard do LangSmith se os prompts foram publicados
3. Deixa-lo público

---

### 4. Iteração

- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.9**

### Critério de Aprovação:

```
- Tone Score >= 0.9
- Acceptance Criteria Score >= 0.9
- User Story Format Score >= 0.9
- Completeness Score >= 0.9

MÉDIA das 4 métricas >= 0.9
```

**IMPORTANTE:** TODAS as 4 métricas devem estar >= 0.9, não apenas a média!

### 5. Testes de Validação

**O que você deve fazer:** Edite o arquivo `tests/test_prompts.py` e implemente, no mínimo, os 6 testes abaixo usando `pytest`:

- `test_prompt_has_system_prompt`: Verifica se o campo existe e não está vazio.
- `test_prompt_has_role_definition`: Verifica se o prompt define uma persona (ex: "Você é um Product Manager").
- `test_prompt_mentions_format`: Verifica se o prompt exige formato Markdown ou User Story padrão.
- `test_prompt_has_few_shot_examples`: Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).
- `test_prompt_no_todos`: Garante que você não esqueceu nenhum `[TODO]` no texto.
- `test_minimum_techniques`: Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas.

**Como validar:**

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

Faça um fork do repositório base: **[Clique aqui para o template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)**

```
desafio-prompt-engineer/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml       # Prompt inicial (após pull)
│   └── bug_to_user_story_v2.yml # Seu prompt otimizado
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith
│   ├── push_prompts.py       # Push ao LangSmith
│   ├── evaluate.py           # Avaliação automática
│   ├── metrics.py            # 4 métricas implementadas
│   ├── dataset.py            # 15 exemplos de bugs
│   └── utils.py              # Funções auxiliares
│
├── tests/
│   └── test_prompts.py       # Testes de validação
│
```

**O que você vai criar:**

- `prompts/bug_to_user_story_v2.yml` - Seu prompt otimizado
- `tests/test_prompts.py` - Seus testes de validação
- `src/pull_prompt.py` Script de pull do repositório da fullcycle
- `src/push_prompt.py` Script de push para o seu repositório
- `README.md` - Documentação do seu processo de otimização

**O que já vem pronto:**

- Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- 4 métricas específicas para Bug to User Story
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/desafio-prompt-engineer/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Ordem de execução

### 1. Executar pull dos prompts ruins

```bash
python src/pull_prompts.py
```

### 2. Refatorar prompts

Edite manualmente o arquivo `prompts/bug_to_user_story_v2.yml` aplicando as técnicas aprendidas no curso.

### 3. Fazer push dos prompts otimizados

```bash
python src/push_prompts.py
```

### 5. Executar avaliação

```bash
python src/evaluate.py
```

---

## Entregável

1. **Repositório público no GitHub** (fork do repositório base) contendo:

   - Todo o código-fonte implementado
   - Arquivo `prompts/bug_to_user_story_v2.yml` 100% preenchido e funcional
   - Arquivo `README.md` atualizado com:

2. **README.md deve conter:**

   A) **Seção "Técnicas Aplicadas (Fase 2)"**:

   - Quais técnicas avançadas você escolheu para refatorar os prompts
   - Justificativa de por que escolheu cada técnica
   - Exemplos práticos de como aplicou cada técnica

   B) **Seção "Resultados Finais"**:

   - Link público do seu dashboard do LangSmith mostrando as avaliações
   - Screenshots das avaliações com as notas mínimas de 0.9 atingidas
   - Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

   C) **Seção "Como Executar"**:

   - Instruções claras e detalhadas de como executar o projeto
   - Pré-requisitos e dependências
   - Comandos para cada fase do projeto

3. **Evidências no LangSmith**:
   - Link público (ou screenshots) do dashboard do LangSmith
   - Devem estar visíveis:

     - Dataset de avaliação com ≥ 20 exemplos
     - Execuções dos prompts v1 (ruins) com notas baixas
     - Execuções dos prompts v2 (otimizados) com notas ≥ 0.9
     - Tracing detalhado de pelo menos 3 exemplos

---

## Técnicas Aplicadas (Fase 2)

### Técnicas escolhidas e justificativas

#### 1. Role Prompting
**O que é:** Define uma persona detalhada para o modelo antes de qualquer instrução.

**Como foi aplicado:**
```
"Você é um Product Owner técnico sênior com 10+ anos de experiência em metodologias ágeis,
especializado em transformar relatos de bugs em User Stories acionáveis para times de desenvolvimento."
```

**Por que escolhi:** O modelo se comporta de forma mais consistente e profissional quando assume um papel específico. Ao definir claramente quem está respondendo (PO técnico sênior), o LLM adota vocabulário ágil preciso, prioriza valor de negócio sobre detalhes de implementação e mantém empatia com o usuário final — critérios diretamente avaliados pelas métricas de Tone e Format.

---

#### 2. Chain of Thought (CoT)
**O que é:** Instrui o modelo a raciocinar passo a passo antes de gerar a resposta final.

**Como foi aplicado:**
```
## PASSO A PASSO — ANALISE ANTES DE ESCREVER

1. IDENTIFIQUE O USUÁRIO: quem é afetado, com contexto específico
2. CLASSIFIQUE A COMPLEXIDADE: SIMPLES / MÉDIO / COMPLEXO
   (para decidir se adiciona seções opcionais de bugs complexos)
3. MAPEIE O BUG: funcionalidade, comportamento atual, esperado, causa raiz
4. LISTE OS DETALHES TÉCNICOS: preserve números, endpoints, logs, valores
5. ESCREVA A USER STORY: focada no objetivo ou necessidade, não na correção técnica
```

**Por que escolhi:** Bugs têm complexidades muito diferentes. Sem etapa de raciocínio explícita, o modelo tende a omitir detalhes técnicos importantes, usar persona genérica ("um usuário") ou enquadrar a user story como "conserto de bug". O CoT força análise sistemática antes de escrever, melhorando F1-Score (recall dos detalhes do bug) e Correctness.

---

#### 3. Few-shot Learning
**O que é:** Fornece exemplos concretos de entrada/saída para calibrar o comportamento esperado.

**Como foi aplicado:** Quatro exemplos completos embutidos no system prompt, cobrindo todos os padrões estruturais do dataset:

- **Exemplo 1 — SIMPLES:** botão que não funciona → apenas User Story + Critérios de Aceitação (sem seção contextual), incluindo critérios implícitos razoáveis (confirmação visual, atualização de contador).
- **Exemplo 2 — MÉDIO Padrão A:** timeout em relatório SQL → User Story + Critérios + `Contexto Técnico:` (uma única seção para bugs com dimensão técnica única: performance, segurança, etc.).
- **Exemplo 3 — MÉDIO Padrão B:** ANR no app Android → User Story + Critérios + `Critérios Técnicos:` (o que implementar) + `Contexto do Bug:` (sintomas atuais) — duas seções separadas para bugs com requisitos de implementação E descrição de sintomas.
- **Exemplo 4 — COMPLEXO:** checkout com múltiplas falhas críticas → frase introdutória + `=== USER STORY PRINCIPAL ===`, critérios categorizados por tema (A/B/C/D), `=== CRITÉRIOS TÉCNICOS ===`, `=== CONTEXTO DO BUG ===`, `=== TASKS TÉCNICAS SUGERIDAS ===`, `=== MÉTRICAS DE SUCESSO ===`.

Cada exemplo demonstra:
- Como escrever o objetivo da user story de forma positiva
- Critérios Given-When-Then na perspectiva do usuário
- Critérios implícitos razoáveis (consistência cross-browser, atualização em tempo real, logs de auditoria)
- A diferença estrutural exata entre SIMPLES, MÉDIO Padrão A, MÉDIO Padrão B e COMPLEXO

**Por que escolhi:** A análise direta das referências do dataset revelou dois problemas de recall críticos: (1) as referências incluem critérios implícitos razoáveis não mencionados explicitamente no bug report (ex: "E o valor deve ser atualizado em tempo real" para bugs de dashboard); (2) bugs médios complexos usam duas seções separadas (`Critérios Técnicos:` + `Contexto do Bug:`) em vez de uma seção genérica `Contexto Técnico:`. Sem exemplos demonstrando esses padrões, o modelo gerava saídas estruturalmente diferentes das referências, reduzindo tanto Recall quanto Precision no avaliador LLM-as-judge.

---

#### 4. Skeleton of Thought
**O que é:** Pré-define a estrutura esquelética adaptativa da resposta por nível de complexidade.

**Como foi aplicado:** Estrutura adaptativa em três formatos fixos, calibrados com base na análise direta das referências do dataset:

**Bugs SIMPLES** — Formato mínimo e limpo:
```
Como um [usuário], eu quero [objetivo], para que [benefício].

Critérios de Aceitação:
- Dado que [contexto]
- Quando [ação]
- Então [resultado]
- E [resultado adicional]
```

**Bugs MÉDIOS** — Adiciona UMA seção contextual com rótulo adaptado ao tipo de bug:
```
[User Story + Critérios de Aceitação]

Contexto Técnico:       ← ou "Contexto de Segurança:", "Contexto do Bug:", "Exemplo de Cálculo:"
- [detalhe técnico]
- [valores/endpoints preservados]
```

**Bugs COMPLEXOS** — User Story introdutória + blocos `===`:
`=== USER STORY PRINCIPAL ===` → `=== CRITÉRIOS DE ACEITAÇÃO ===` (categorizados A/B/C/D) → `=== CRITÉRIOS TÉCNICOS ===` → `=== CONTEXTO DO BUG ===` → `=== TASKS TÉCNICAS SUGERIDAS ===` → `=== MÉTRICAS DE SUCESSO ===` (quando métricas disponíveis)

**Por que escolhi:** A análise direta de todas as referências do dataset revelou padrões precisos:
- Nenhuma referência de bug SIMPLES ou MÉDIO usa headers `##` (Markdown)
- Bugs simples têm APENAS User Story + Critérios — nenhuma seção contextual, mesmo com números específicos ou comparações de plataforma
- Bugs médios usam **rótulo adaptativo** ao tipo de bug: `Contexto Técnico:` (performance/integração), `Contexto de Segurança:` (vulnerabilidades), `Exemplo de Cálculo:` (bugs de lógica matemática), `Critérios Técnicos:` + `Contexto do Bug:` (bugs com requisitos de implementação + sintomas)
- Bugs com múltiplos perfis de usuário usam `Critérios Adicionais para [Perfil]:` antes da seção contextual

O Skeleton of Thought correto espelha exatamente esses padrões: estrutura adaptativa por complexidade e tipo, sem Markdown, com seções contextuais precisas.

---

## Resultados Finais

> Preencha esta seção após executar a avaliação final com `python src/evaluate.py`

### Tabela comparativa: v1 vs v2

| Métrica             | v1 (baseline) | v2 (otimizado) | Meta  |
|---------------------|---------------|----------------|-------|
| Helpfulness         | —             | —              | ≥ 0.9 |
| Correctness         | —             | —              | ≥ 0.9 |
| F1-Score            | —             | —              | ≥ 0.9 |
| Clarity             | —             | —              | ≥ 0.9 |
| Precision           | —             | —              | ≥ 0.9 |
| **Média Geral**     | —             | —              | ≥ 0.9 |

### Dashboard LangSmith

> Adicione aqui o link público e screenshots do dashboard do LangSmith.

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) com API Key
- API Key da OpenAI **ou** Google Gemini

### Configuração

```bash
# 1. Clone o repositório e instale dependências
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves: LANGSMITH_API_KEY, OPENAI_API_KEY (ou GOOGLE_API_KEY), LLM_PROVIDER
```

### Execução

```bash
# Pull dos prompts do LangSmith
python src/pull_prompts.py

# Push do prompt otimizado para o LangSmith
python src/push_prompts.py

# Avaliação do prompt
python src/evaluate.py

# Testes de validação
pytest tests/test_prompts.py -v
```

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de PRs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.9 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final
