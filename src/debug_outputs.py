"""
Script de diagnóstico: compara output do modelo com referência para cada exemplo.

Carrega o prompt do YAML LOCAL (sem necessidade de push ao LangSmith Hub),
roda os 10 exemplos de avaliação e exibe:
  - Output gerado pelo modelo
  - Referência esperada
  - F1 com decomposição Precision/Recall + reasoning do juiz (GPT-4o)

Útil para identificar exatamente o que o modelo está errando antes de
fazer mudanças no prompt.

Uso:
    poetry run python src/debug_outputs.py
    poetry run python src/debug_outputs.py --example 6   # apenas exemplo 6
    poetry run python src/debug_outputs.py --save        # salva em debug_output.txt
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

sys.path.insert(0, str(Path(__file__).parent))

from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, get_llm
from metrics import evaluate_f1_score


YAML_PATH = "prompts/bug_to_user_story_v2.yml"
DATASET_PATH = "datasets/bug_to_user_story.jsonl"
PROMPT_NAME = "bug_to_user_story_v2"


def load_prompt_from_yaml(yaml_path: str) -> ChatPromptTemplate:
    data = load_yaml(yaml_path)
    if not data or PROMPT_NAME not in data:
        raise ValueError(f"Prompt '{PROMPT_NAME}' não encontrado em {yaml_path}")
    prompt_data = data[PROMPT_NAME]
    return ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])


def load_examples(jsonl_path: str, max_examples: int = 10):
    examples = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ex = json.loads(line)
                if "bug_report" in ex.get("inputs", {}) and ex.get("outputs", {}).get("reference"):
                    examples.append(ex)
    return examples[:max_examples]


def divider(char="-", width=80):
    return char * width


def format_block(label: str, text: str, width: int = 80) -> str:
    lines = [f"  {l}" for l in text.splitlines()]
    body = "\n".join(lines)
    return f"{'[ ' + label + ' ]':>{width}}\n{body}"


def run_diagnosis(example_filter: int = None, save: bool = False):
    print(divider("="))
    print("DEBUG: OUTPUT DO MODELO vs REFERÊNCIA")
    print(divider("="))
    print(f"Prompt:  {YAML_PATH} (local, sem push necessário)")
    print(f"Dataset: {DATASET_PATH}")
    print(f"Modelo principal: {os.getenv('LLM_MODEL', 'gpt-4o-mini')}")
    print(f"Modelo avaliador: {os.getenv('EVAL_MODEL', 'gpt-4o')}")
    print()

    prompt_template = load_prompt_from_yaml(YAML_PATH)
    llm = get_llm(temperature=0)
    chain = prompt_template | llm

    examples = load_examples(DATASET_PATH)
    print(f"Exemplos carregados: {len(examples)}\n")

    output_lines = []

    def out(text=""):
        print(text)
        output_lines.append(text)

    for i, ex in enumerate(examples, 1):
        if example_filter is not None and i != example_filter:
            continue

        bug_report = ex["inputs"]["bug_report"]
        reference = ex["outputs"]["reference"]
        meta = ex.get("metadata", {})
        complexity = meta.get("complexity", "?")
        bug_type = meta.get("type", "?")

        out(divider("="))
        out(f"EXEMPLO {i}/10  |  complexidade: {complexity}  |  tipo: {bug_type}")
        out(divider("="))

        # --- BUG REPORT ---
        out("\n[BUG REPORT]")
        for line in bug_report.splitlines():
            out(f"  {line}")

        # --- Gerar output ---
        response = chain.invoke({"bug_report": bug_report})
        model_output = response.content

        # --- MODEL OUTPUT ---
        out(f"\n{divider('-')}")
        out("[MODEL OUTPUT]")
        for line in model_output.splitlines():
            out(f"  {line}")

        # --- REFERENCE ---
        out(f"\n{divider('-')}")
        out("[REFERENCE]")
        for line in reference.splitlines():
            out(f"  {line}")

        # --- F1 com P/R e reasoning ---
        out(f"\n{divider('-')}")
        out("[AVALIAÇÃO F1]")
        f1_result = evaluate_f1_score(bug_report, model_output, reference)
        f1 = f1_result["score"]
        prec = f1_result["precision"]
        rec = f1_result["recall"]
        f1_sym = "✓" if f1 >= 0.9 else "✗"
        out(f"  F1={f1:.2f} {f1_sym}  |  Precision={prec:.2f}  |  Recall={rec:.2f}")
        out(f"  Reasoning: {f1_result['reasoning']}")
        out()

    out(divider("="))
    out("FIM DO DIAGNÓSTICO")
    out(divider("="))

    if save:
        output_path = Path("debug_output.txt")
        output_path.write_text("\n".join(output_lines), encoding="utf-8")
        print(f"\nSalvo em: {output_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico de outputs do modelo vs referência")
    parser.add_argument("--example", type=int, default=None, help="Número do exemplo (1-10). Omitir = todos.")
    parser.add_argument("--save", action="store_true", help="Salvar output em debug_output.txt")
    args = parser.parse_args()

    run_diagnosis(example_filter=args.example, save=args.save)


if __name__ == "__main__":
    main()
