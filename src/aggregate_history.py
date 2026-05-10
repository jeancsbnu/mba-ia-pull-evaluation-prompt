"""Aggregate F1/Precision/Recall per example across all debug files + extract patterns from judge reasoning."""
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

debug_files = sorted(Path(".").glob("debug_bug_to_user_story_v2-*.txt"))

# data[ex_idx][run_label] = (f1, p, r, reasoning)
data = defaultdict(dict)
runs = []

for f in debug_files:
    label = f.stem.replace("debug_bug_to_user_story_v2-", "")
    runs.append(label)
    text = f.read_text(encoding="utf-8")
    blocks = re.split(r"={80}\nEXEMPLO (\d+)", text)
    for i in range(1, len(blocks), 2):
        ex_idx = int(blocks[i])
        block = blocks[i + 1]
        m = re.search(r"F1=([\d.]+).*?Precision=([\d.]+).*?Recall=([\d.]+)", block)
        if not m:
            continue
        f1, p, r = float(m.group(1)), float(m.group(2)), float(m.group(3))
        rmatch = re.search(r"Reasoning: (.+?)(?:\n={80}|\Z)", block, re.DOTALL)
        reasoning = rmatch.group(1).strip()[:300] if rmatch else ""
        data[ex_idx][label] = (f1, p, r, reasoning)

# Skip 191535 (earliest, may be incomplete)
ordered_runs = [r for r in runs if data.get(1, {}).get(r) is not None]

print("=" * 100)
print("F1 PER EXAMPLE ACROSS RUNS")
print("=" * 100)
print(f"{'Run':<25}", end="")
for ex in range(1, 11):
    print(f"  Ex{ex:<2}", end="")
print()
print("-" * 100)
for r in ordered_runs:
    print(f"{r:<25}", end="")
    for ex in range(1, 11):
        v = data.get(ex, {}).get(r)
        s = f"{v[0]:.2f}" if v else "  - "
        marker = "✓" if v and v[0] >= 0.9 else " "
        print(f"  {s}{marker}", end="")
    avg = sum(data[ex][r][0] for ex in range(1, 11) if r in data[ex]) / 10
    print(f"  | avg={avg:.3f}")

print()
print("=" * 100)
print("STABILIDADE POR EXEMPLO (mín / média / máx / desvio)")
print("=" * 100)
for ex in range(1, 11):
    f1s = [v[0] for v in data[ex].values()]
    if not f1s:
        continue
    mn, mx = min(f1s), max(f1s)
    avg = sum(f1s) / len(f1s)
    spread = mx - mn
    flag = " (instável)" if spread >= 0.2 else (" (preso baixo)" if mx <= 0.85 else "")
    print(f"  Ex {ex}: min={mn:.2f}  avg={avg:.2f}  max={mx:.2f}  spread={spread:.2f}{flag}")

print()
print("=" * 100)
print("PIORES EXEMPLOS (média < 0.85) — KEYWORDS COMUNS NO REASONING")
print("=" * 100)
keywords = ["persona", "CRDT", "Vector clocks", "TTL", "Materialized", "DOMPurify",
            "CSP", "Content Security", "polling", "idempotency", "estoque", "remover",
            "aguardar", "Cliente A", "Usuário A", "exportação", "CSV", "notifica",
            "estratégia", "auto-merge", "sistema de e-commerce", "executivo", "gerente"]
for ex in range(1, 11):
    f1s = [v[0] for v in data[ex].values()]
    avg = sum(f1s) / len(f1s) if f1s else 0
    if avg >= 0.85:
        continue
    print(f"\n  Ex {ex} (média {avg:.2f}):")
    counts = defaultdict(int)
    for label, (_, _, _, reasoning) in data[ex].items():
        for k in keywords:
            if k.lower() in reasoning.lower():
                counts[k] += 1
    sorted_counts = sorted(counts.items(), key=lambda x: -x[1])
    for k, c in sorted_counts[:8]:
        print(f"    - '{k}' citado em {c}/{len(f1s)} runs")

print()
print("=" * 100)
print("ÚLTIMA REGRESSÃO POR EXEMPLO (run mais recente vs penúltimo)")
print("=" * 100)
if len(ordered_runs) >= 2:
    last, prev = ordered_runs[-1], ordered_runs[-2]
    print(f"\nÚltimo: {last}")
    print(f"Penúltimo: {prev}\n")
    for ex in range(1, 11):
        v_last = data[ex].get(last, (None,))[0]
        v_prev = data[ex].get(prev, (None,))[0]
        if v_last is None or v_prev is None:
            continue
        delta = v_last - v_prev
        marker = "↑" if delta > 0.02 else ("↓" if delta < -0.02 else "=")
        print(f"  Ex {ex}: {v_prev:.2f} → {v_last:.2f}  ({marker} {delta:+.2f})")
