A) **Seção "Técnicas Aplicadas (Fase 2)"**:

- Quais técnicas avançadas você escolheu para refatorar os prompts
  R: Role Prompting e Skeleton of Thought

- Justificativa de por que escolheu cada técnica
  R: Role Prompting - Isso guia o modelo a responder com linguagem e estrutura adequadas.
     Skeleton of Thought - Isso ajuda o modelo a pensar passo a passo e a estruturar a resposta de forma clara.

- Exemplos práticos de como aplicou cada técnica
  R: Role Prompting - "Você é um Product Owner técnico especializado..."
     Skeleton of Thought - Define passos explícitos (1, 2, 3) e Define estrutura obrigatória da resposta (Título, User Story, Descrição, etc.)

   B) **Seção "Resultados Finais"**:

   - Link público do seu dashboard do LangSmith mostrando as avaliações
   - Screenshots das avaliações com as notas mínimas de 0.9 atingidas
   - Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

   C) **Seção "Como Executar"**:

   1) Executar o pull para pegar os prompts iniciais - pull_prompts.py
   2) Executar a otimização dos prompts
   3) Executar o push para enviar os prompts otimizados
   4) Executar a avaliação para verificar as métricas

3. **Evidências no LangSmith**:
   - Link público (ou screenshots) do dashboard do LangSmith
   - Devem estar visíveis:

     - Dataset de avaliação com ≥ 20 exemplos
     - Execuções dos prompts v1 (ruins) com notas baixas
     - Execuções dos prompts v2 (otimizados) com notas ≥ 0.9
     - Tracing detalhado de pelo menos 3 exemplos

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de PRs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.9 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final
