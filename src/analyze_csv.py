"""
Analisa CSV exportado do LangSmith e computa F1 (Precision/Recall) por exemplo.

Não re-executa o modelo principal — usa os outputs já calculados no CSV.
Só chama o LLM juiz para avaliar os outputs existentes.

Uso:
    poetry run python src/analyze_csv.py caminho/para/arquivo.csv
    poetry run python src/analyze_csv.py caminho/para/arquivo.csv --example 6
    poetry run python src/analyze_csv.py caminho/para/arquivo.csv --save
"""

import csv
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from metrics import evaluate_f1_score


def parse_json_cell(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}


def load_csv_examples(csv_path: str) -> list[dict]:
    examples = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            inputs = parse_json_cell(row.get("inputs", "{}"))
            refs = parse_json_cell(row.get("reference_outputs", "{}"))
            outs = parse_json_cell(row.get("outputs", "{}"))

            bug_report = inputs.get("bug_report", "")
            reference = refs.get("reference", "")
            output = outs.get("output", "")

            if not bug_report or not reference or not output:
                continue

            examples.append({
                "index": i,
                "bug_report": bug_report,
                "reference": reference,
                "output": output,
                "latency": row.get("latency", ""),
                "tokens": row.get("tokens", ""),
            })
    return examples


def divider(char="-", width=80):
    return char * width


def run_analysis(csv_path: str, example_filter: int = None, save: bool = False):
    examples = load_csv_examples(csv_path)
    if not examples:
        print("Nenhum exemplo encontrado no CSV.")
        return

    print(divider("="))
    print("ANÁLISE POR EXEMPLO — CSV do LangSmith")
    print(divider("="))
    print(f"Arquivo: {csv_path}")
    print(f"Exemplos encontrados: {len(examples)}")
    print()

    output_lines = []

    def out(text=""):
        print(text)
        output_lines.append(text)

    scores = []

    for ex in examples:
        i = ex["index"]
        if example_filter is not None and i != example_filter:
            continue

        out(divider("="))
        out(f"EXEMPLO {i}  |  latência: {ex['latency'][:5]}s  |  tokens: {ex['tokens']}")
        out(divider("="))

        out("\n[BUG REPORT]")
        for line in ex["bug_report"][:500].splitlines():
            out(f"  {line}")
        if len(ex["bug_report"]) > 500:
            out("  (...)")

        out(f"\n{divider('-')}")
        out("[OUTPUT DO MODELO]")
        for line in ex["output"][:800].splitlines():
            out(f"  {line}")
        if len(ex["output"]) > 800:
            out("  (...)")

        out(f"\n{divider('-')}")
        out("[REFERÊNCIA]")
        for line in ex["reference"][:800].splitlines():
            out(f"  {line}")
        if len(ex["reference"]) > 800:
            out("  (...)")

        out(f"\n{divider('-')}")
        out("[AVALIAÇÃO F1]")
        result = evaluate_f1_score(ex["bug_report"], ex["output"], ex["reference"])
        f1 = result["score"]
        prec = result["precision"]
        rec = result["recall"]
        sym = "✓" if f1 >= 0.9 else "✗"
        out(f"  F1={f1:.2f} {sym}  |  Precision={prec:.2f}  |  Recall={rec:.2f}")
        out(f"  Reasoning: {result['reasoning']}")
        out()

        scores.append({"index": i, "f1": f1, "precision": prec, "recall": rec})

    if len(scores) > 1:
        out(divider("="))
        out("RESUMO")
        out(divider("="))
        out(f"  {'Ex':<4}  {'F1':>6}  {'P':>6}  {'R':>6}")
        out(f"  {divider('-', 28)}")
        for s in sorted(scores, key=lambda x: x["f1"]):
            sym = "✓" if s["f1"] >= 0.9 else "✗"
            out(f"  {s['index']:<4}  {s['f1']:.2f} {sym}  {s['precision']:.2f}  {s['recall']:.2f}")
        avg_f1 = sum(s["f1"] for s in scores) / len(scores)
        out(f"  {divider('-', 28)}")
        out(f"  {'MÉDIA':<4}  {avg_f1:.2f}    {'✓' if avg_f1 >= 0.9 else '✗'}")
        out()
        worst = sorted(scores, key=lambda x: x["f1"])[:3]
        out(f"  Piores exemplos: {[s['index'] for s in worst]}")

    out(divider("="))

    if save:
        stem = Path(csv_path).stem
        out_path = Path(f"debug_{stem}.txt")
        out_path.write_text("\n".join(output_lines), encoding="utf-8")
        print(f"\nSalvo em: {out_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Analisa CSV do LangSmith com F1 por exemplo")
    parser.add_argument("csv_path", help="Caminho para o CSV exportado do LangSmith")
    parser.add_argument("--example", type=int, default=None, help="Analisar apenas o exemplo N")
    parser.add_argument("--save", action="store_true", help="Salvar output em debug_<nome>.txt")
    args = parser.parse_args()

    run_analysis(args.csv_path, example_filter=args.example, save=args.save)


if __name__ == "__main__":
    main()
