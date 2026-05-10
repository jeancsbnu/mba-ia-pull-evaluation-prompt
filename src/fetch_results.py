"""
Busca e exibe os resultados de avaliações do LangSmith.

Mostra os experimentos mais recentes e suas métricas agregadas.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from datetime import datetime, timezone

_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

sys.stdout.reconfigure(encoding='utf-8')


def format_score(score):
    if score is None:
        return "   —   "
    symbol = "✓" if score >= 0.9 else "✗"
    return f"{score:.4f} {symbol}"


def fetch_evaluation_results():
    api_key = os.getenv("LANGSMITH_API_KEY")
    project_name = os.getenv("LANGCHAIN_PROJECT", "prompt-optimization-challenge-resolved")
    dataset_name = f"{project_name}-eval"

    if not api_key:
        print("❌ LANGSMITH_API_KEY não configurada no .env")
        return

    client = Client(api_key=api_key)

    print("=" * 70)
    print("RESULTADOS DE AVALIAÇÕES — LangSmith")
    print("=" * 70)
    print(f"Dataset: {dataset_name}\n")

    # Listar todos os projetos que referenciam o dataset de avaliação
    try:
        datasets = list(client.list_datasets(dataset_name=dataset_name))
        if not datasets:
            print(f"❌ Dataset '{dataset_name}' não encontrado.")
            return

        dataset = datasets[0]
        dataset_id = str(dataset.id)
        print(f"✓ Dataset encontrado: {dataset.name}")
        print(f"  ID: {dataset_id}")
        print(f"  Exemplos: {dataset.example_count if hasattr(dataset, 'example_count') else '?'}\n")
    except Exception as e:
        print(f"❌ Erro ao buscar dataset: {e}")
        return

    # Listar projetos (experimentos) vinculados ao dataset
    try:
        projects = list(client.list_projects(reference_dataset_id=dataset_id))
        if not projects:
            print("Nenhum experimento de avaliação encontrado para este dataset.")
            print("\nExecute primeiro: python src/evaluate.py")
            return
    except Exception as e:
        print(f"❌ Erro ao listar experimentos: {e}")
        return

    # Ordenar por data de criação (mais recente primeiro)
    projects = sorted(projects, key=lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    print(f"Experimentos encontrados: {len(projects)}")
    print("-" * 70)

    metric_keys = ["f1_score", "clarity", "precision", "helpfulness", "correctness",
                   "f1-score", "tone_score", "acceptance_criteria_score",
                   "user_story_format_score", "completeness_score"]

    for proj in projects[:5]:  # Mostrar apenas os 5 mais recentes
        created = proj.created_at.strftime("%Y-%m-%d %H:%M") if proj.created_at else "?"
        print(f"\n📊 Experimento: {proj.name}")
        print(f"   Criado em:   {created}")

        # Buscar runs do projeto para extrair feedback/scores
        try:
            runs = list(client.list_runs(project_name=proj.name, run_type="chain", limit=200))
            if not runs:
                runs = list(client.list_runs(project_name=proj.name, limit=200))

            # Coletar feedback de cada run
            scores_by_key = {}
            runs_with_feedback = 0

            for run in runs:
                feedback_list = list(client.list_feedback(run_ids=[str(run.id)]))
                if feedback_list:
                    runs_with_feedback += 1
                    for fb in feedback_list:
                        key = fb.key.lower().replace("-", "_").replace(" ", "_")
                        if fb.score is not None:
                            if key not in scores_by_key:
                                scores_by_key[key] = []
                            scores_by_key[key].append(float(fb.score))

            if scores_by_key:
                print(f"   Runs com feedback: {runs_with_feedback}/{len(runs)}")
                print(f"   Métricas:")

                all_averages = []
                for key, values in sorted(scores_by_key.items()):
                    avg = sum(values) / len(values)
                    all_averages.append(avg)
                    print(f"     - {key:<35} {format_score(avg)}")

                if all_averages:
                    overall = sum(all_averages) / len(all_averages)
                    print(f"\n   {'MÉDIA GERAL':<37} {format_score(overall)}")
            else:
                print(f"   Runs encontrados: {len(runs)} (sem feedback registrado)")
                print("   ℹ️  Os scores são calculados localmente pelo evaluate.py")
                print("      e não são enviados automaticamente ao LangSmith.")

        except Exception as e:
            print(f"   ⚠️  Erro ao buscar runs: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    fetch_evaluation_results()
