"""
Script para avaliar prompts otimizados via langsmith.evaluate().

Este script:
1. Carrega dataset de avaliação de arquivo .jsonl (datasets/bug_to_user_story.jsonl)
2. Cria/reutiliza dataset no LangSmith
3. Puxa prompts otimizados do LangSmith Hub (fonte única de verdade)
4. Executa langsmith.evaluate() — cria Experiments visíveis no dashboard
5. Calcula 5 métricas: Helpfulness, Correctness, F1-Score, Clarity, Precision
6. Exibe resumo no terminal

Cada execução gera um Experiment único (timestamp no prefix), sem sobrescrever runs anteriores.

Suporta múltiplos providers de LLM:
- OpenAI (gpt-4o, gpt-4o-mini)
- Google Gemini (gemini-1.5-flash, gemini-1.5-pro)

Configure o provider no arquivo .env através da variável LLM_PROVIDER.
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import traceback
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate

from utils import check_env_vars, format_score, print_section_header, get_llm as get_configured_llm
from metrics import evaluate_f1_score, evaluate_clarity, evaluate_precision

load_dotenv()


# ─────────────────────────────────────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────────────────────────────────────

def get_llm():
    """Retorna LLM principal com temperatura 0 (respostas determinísticas)."""
    return get_configured_llm(temperature=0)


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────

def load_dataset_from_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    """Carrega exemplos de arquivo JSONL."""
    examples = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    examples.append(json.loads(line))
        return examples
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        print("\nCertifique-se de que o arquivo datasets/bug_to_user_story.jsonl existe.")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSONL: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return []


def create_evaluation_dataset(client: Client, dataset_name: str, jsonl_path: str) -> str:
    """Cria dataset no LangSmith ou reutiliza existente."""
    print(f"Verificando dataset: {dataset_name}...")

    examples = load_dataset_from_jsonl(jsonl_path)
    if not examples:
        print("❌ Nenhum exemplo carregado do arquivo .jsonl")
        return dataset_name

    print(f"   ✓ {len(examples)} exemplos encontrados em {jsonl_path}")

    try:
        existing = next(
            (ds for ds in client.list_datasets(dataset_name=dataset_name)
             if ds.name == dataset_name),
            None
        )

        if existing:
            print(f"   ✓ Dataset '{dataset_name}' já existe, usando existente")
        else:
            dataset = client.create_dataset(dataset_name=dataset_name)
            for example in examples:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example["inputs"],
                    outputs=example["outputs"]
                )
            print(f"   ✓ Dataset criado com {len(examples)} exemplos")

    except Exception as e:
        print(f"   ⚠️  Erro ao criar dataset: {e}")

    return dataset_name


# ─────────────────────────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────────────────────────

def pull_prompt_from_langsmith(prompt_name: str) -> ChatPromptTemplate:
    """Puxa prompt do LangSmith Hub com mensagens de erro detalhadas."""
    try:
        print(f"   Puxando prompt do LangSmith Hub: {prompt_name}")
        prompt = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso")
        return prompt

    except Exception as e:
        error_msg = str(e).lower()

        print(f"\n{'=' * 70}")
        print(f"❌ ERRO: Não foi possível carregar o prompt '{prompt_name}'")
        print(f"{'=' * 70}\n")

        if "not found" in error_msg or "404" in error_msg:
            print("⚠️  O prompt não foi encontrado no LangSmith Hub.\n")
            print("AÇÕES NECESSÁRIAS:")
            print("1. Verifique se você já fez push do prompt otimizado:")
            print(f"   python src/push_prompts.py")
            print()
            print("2. Confirme se o prompt foi publicado com sucesso em:")
            print(f"   https://smith.langchain.com/prompts")
            print()
            print(f"3. Certifique-se de que o nome do prompt está correto: '{prompt_name}'")
            print()
            print("4. Se você alterou o prompt no YAML, refaça o push:")
            print(f"   python src/push_prompts.py")
        else:
            print(f"Erro técnico: {e}\n")
            print("Verifique:")
            print("- LANGSMITH_API_KEY está configurada corretamente no .env")
            print("- Você tem acesso ao workspace do LangSmith")
            print("- Sua conexão com a internet está funcionando")

        print(f"\n{'=' * 70}\n")
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Função de predição (app)
# ─────────────────────────────────────────────────────────────────────────────

def make_predict(prompt_template: ChatPromptTemplate, llm):
    """
    Retorna a função predict usada pelo langsmith.evaluate().

    O langsmith.evaluate() passa o campo `inputs` de cada exemplo do dataset
    e espera um dict de saída. O closure captura prompt_template e llm.
    """
    chain = prompt_template | llm

    def predict(inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = chain.invoke(inputs)
            answer = response.content if hasattr(response, 'content') else str(response)
            return {"output": answer}
        except Exception as e:
            # Retorna output vazio para não quebrar o experimento.
            # Os evaluators tratam output vazio retornando score 0.0.
            print(f"   ⚠️  Erro na predição: {e}")
            print(f"   {traceback.format_exc()}")
            return {"output": ""}

    return predict


# ─────────────────────────────────────────────────────────────────────────────
# Evaluators
# ─────────────────────────────────────────────────────────────────────────────

def _extract_run_data(run, example) -> tuple:
    """
    Extrai (output, question, reference) do par run/example fornecido pelo
    langsmith.evaluate():
    - run.outputs: saída produzida pelo predict()
    - example.inputs: inputs do dataset (bug_report, question, etc.)
    - example.outputs: referência esperada do dataset
    """
    output = (run.outputs or {}).get("output", "")
    inputs = example.inputs or {}
    question = inputs.get("bug_report", inputs.get("question", inputs.get("pr_title", "")))
    reference = (example.outputs or {}).get("reference", "")
    return output, question, reference


def evaluator_f1(run, example) -> Dict[str, Any]:
    """Calcula F1-Score via LLM-as-Judge."""
    output, question, reference = _extract_run_data(run, example)
    if not output or not reference:
        return {"key": "f1_score", "score": 0.0}
    result = evaluate_f1_score(question, output, reference)
    return {"key": "f1_score", "score": result["score"]}


def evaluator_clarity(run, example) -> Dict[str, Any]:
    """Avalia Clarity via LLM-as-Judge."""
    output, question, reference = _extract_run_data(run, example)
    if not output or not reference:
        return {"key": "clarity", "score": 0.0}
    result = evaluate_clarity(question, output, reference)
    return {"key": "clarity", "score": result["score"]}


def evaluator_precision(run, example) -> Dict[str, Any]:
    """Avalia Precision via LLM-as-Judge."""
    output, question, reference = _extract_run_data(run, example)
    if not output or not reference:
        return {"key": "precision", "score": 0.0}
    result = evaluate_precision(question, output, reference)
    return {"key": "precision", "score": result["score"]}


# ─────────────────────────────────────────────────────────────────────────────
# Orquestração do experimento
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_prompt(
    prompt_name: str,
    dataset_name: str,
    client: Client
) -> Dict[str, float]:
    """
    Executa avaliação via langsmith.evaluate() e cria um Experiment no LangSmith.

    Mantém a mesma saída do terminal (progresso [i/N] por exemplo).
    O experiment_prefix inclui timestamp para garantir que cada execução
    gere um Experiment único — nenhuma run sobrescreve outra.

    Returns:
        Dicionário com scores médios: f1_score, clarity, precision,
        helpfulness, correctness.
    """
    print(f"\n🔍 Avaliando: {prompt_name}")

    prompt_template = pull_prompt_from_langsmith(prompt_name)

    # Filtra apenas exemplos com bug_report e reference (mesma lógica do original)
    all_examples = list(client.list_examples(dataset_name=dataset_name))
    valid_examples = [e for e in all_examples
                      if isinstance(e.inputs, dict) and "bug_report" in e.inputs
                      and isinstance(e.outputs, dict) and e.outputs.get("reference")]
    examples_to_eval = valid_examples[:10]
    total = len(examples_to_eval)

    print(f"   Dataset: {len(all_examples)} exemplos ({len(valid_examples)} com bug_report e reference)")

    llm = get_llm()
    predict = make_predict(prompt_template, llm)

    # Prefix único por execução — garante novo Experiment no LangSmith a cada run
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    experiment_prefix = f"{prompt_name}-{timestamp}"

    print("   Avaliando exemplos...")

    try:
        results = evaluate(
            predict,
            data=examples_to_eval,  # apenas os exemplos filtrados
            evaluators=[
                evaluator_f1,
                evaluator_clarity,
                evaluator_precision,
            ],
            experiment_prefix=experiment_prefix,
            description=(
                f"Avaliação automática do prompt '{prompt_name}' "
                f"em {datetime.now().isoformat()}"
            ),
            max_concurrency=2,
        )

        # Itera resultados por exemplo, imprime progresso e coleta scores
        f1_scores, clarity_scores, precision_scores = [], [], []

        for i, row in enumerate(results, 1):
            # Extrai lista de EvaluationResult do row
            if isinstance(row, dict):
                eval_results = row.get("evaluation_results", {}).get("results", [])
            else:
                eval_results = getattr(getattr(row, "evaluation_results", None), "results", [])

            scores_by_key: Dict[str, float] = {}
            for er in eval_results:
                key = getattr(er, "key", None) or (er.get("key") if isinstance(er, dict) else None)
                score = getattr(er, "score", None)
                if score is None and isinstance(er, dict):
                    score = er.get("score")
                if key and score is not None:
                    scores_by_key[key] = float(score)

            f1 = scores_by_key.get("f1_score", 0.0)
            clarity = scores_by_key.get("clarity", 0.0)
            precision = scores_by_key.get("precision", 0.0)

            f1_scores.append(f1)
            clarity_scores.append(clarity)
            precision_scores.append(precision)

            print(f"      [{i}/{total}] F1:{f1:.2f} Clarity:{clarity:.2f} Precision:{precision:.2f}")

        avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0.0
        avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0

        avg_helpfulness = (avg_clarity + avg_precision) / 2
        avg_correctness = (avg_f1 + avg_precision) / 2

        return {
            "helpfulness": round(avg_helpfulness, 4),
            "correctness": round(avg_correctness, 4),
            "f1_score": round(avg_f1, 4),
            "clarity": round(avg_clarity, 4),
            "precision": round(avg_precision, 4),
        }

    except Exception as e:
        print(f"   ❌ Erro ao executar experimento: {e}")
        print(f"   {traceback.format_exc()}")
        return {k: 0.0 for k in ["helpfulness", "correctness", "f1_score", "clarity", "precision"]}


# ─────────────────────────────────────────────────────────────────────────────
# Exibição de resultados
# ─────────────────────────────────────────────────────────────────────────────

def display_results(prompt_name: str, scores: Dict[str, float]) -> bool:
    """Exibe scores formatados no terminal e retorna se aprovado (média >= 0.9)."""
    print("\n" + "=" * 50)
    print(f"Prompt: {prompt_name}")
    print("=" * 50)

    print("\nMétricas LangSmith:")
    print(f"  - Helpfulness: {format_score(scores['helpfulness'], threshold=0.9)}")
    print(f"  - Correctness: {format_score(scores['correctness'], threshold=0.9)}")

    print("\nMétricas Customizadas:")
    print(f"  - F1-Score:    {format_score(scores['f1_score'], threshold=0.9)}")
    print(f"  - Clarity:     {format_score(scores['clarity'], threshold=0.9)}")
    print(f"  - Precision:   {format_score(scores['precision'], threshold=0.9)}")

    average_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 50)
    print(f"MÉDIA GERAL: {average_score:.4f}")
    print("-" * 50)

    passed = average_score >= 0.9
    if passed:
        print(f"\n✅ STATUS: APROVADO (média >= 0.9)")
    else:
        print(f"\n❌ STATUS: REPROVADO (média < 0.9)")
        print(f"⚠️  Média atual: {average_score:.4f} | Necessário: 0.9000")

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print_section_header("AVALIAÇÃO DE PROMPTS OTIMIZADOS")

    provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")

    print(f"Provider: {provider}")
    print(f"Modelo Principal: {llm_model}")
    print(f"Modelo de Avaliação: {eval_model}\n")

    required_vars = ["LANGSMITH_API_KEY", "LLM_PROVIDER"]
    if provider == "openai":
        required_vars.append("OPENAI_API_KEY")
    elif provider in ["google", "gemini"]:
        required_vars.append("GOOGLE_API_KEY")

    if not check_env_vars(required_vars):
        return 1

    client = Client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "prompt-optimization-challenge-resolved")

    jsonl_path = "datasets/bug_to_user_story.jsonl"

    if not Path(jsonl_path).exists():
        print(f"❌ Arquivo de dataset não encontrado: {jsonl_path}")
        print("\nCertifique-se de que o arquivo existe antes de continuar.")
        return 1

    dataset_name = f"{project_name}-eval"
    create_evaluation_dataset(client, dataset_name, jsonl_path)

    print("\n" + "=" * 70)
    print("EXECUTANDO EXPERIMENTOS NO LANGSMITH")
    print("=" * 70)
    print("\nCertifique-se de ter feito push dos prompts antes de avaliar:")
    print("  python src/push_prompts.py\n")
    print("Cada execução cria um Experiment único (timestamp no prefix).")
    print(f"Acompanhe em: https://smith.langchain.com/o/projects\n")

    prompts_to_evaluate = [
        "bug_to_user_story_v2",
    ]

    all_passed = True
    evaluated_count = 0
    results_summary = []

    for prompt_name in prompts_to_evaluate:
        evaluated_count += 1

        try:
            scores = evaluate_prompt(prompt_name, dataset_name, client)
            passed = display_results(prompt_name, scores)
            all_passed = all_passed and passed
            results_summary.append({"prompt": prompt_name, "scores": scores, "passed": passed})

        except Exception as e:
            print(f"\n❌ Falha ao avaliar '{prompt_name}': {e}")
            all_passed = False
            results_summary.append({
                "prompt": prompt_name,
                "scores": {k: 0.0 for k in ["helpfulness", "correctness", "f1_score", "clarity", "precision"]},
                "passed": False,
            })

    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50 + "\n")

    if evaluated_count == 0:
        print("⚠️  Nenhum prompt foi avaliado")
        return 1

    print(f"Prompts avaliados: {evaluated_count}")
    print(f"Aprovados: {sum(1 for r in results_summary if r['passed'])}")
    print(f"Reprovados: {sum(1 for r in results_summary if not r['passed'])}\n")

    if all_passed:
        print("✅ Todos os prompts atingiram média >= 0.9!")
        print(f"\n✓ Confira os resultados em:")
        print(f"  https://smith.langchain.com/projects/{project_name}")
        print("\nPróximos passos:")
        print("1. Documente o processo no README.md")
        print("2. Capture screenshots das avaliações")
        print("3. Faça commit e push para o GitHub")
        return 0
    else:
        print("⚠️  Alguns prompts não atingiram média >= 0.9")
        print("\nPróximos passos:")
        print("1. Refatore os prompts com score baixo")
        print("2. Faça push novamente: python src/push_prompts.py")
        print("3. Execute: python src/evaluate.py novamente")
        return 1


if __name__ == "__main__":
    sys.exit(main())
