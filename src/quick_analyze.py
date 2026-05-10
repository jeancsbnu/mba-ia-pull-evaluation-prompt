"""Quick analysis of LangSmith CSV — reads existing scores and computes aggregates."""
import csv
import sys
import json
from pathlib import Path

path = sys.argv[1] if len(sys.argv) > 1 else "D:/temp/bug_to_user_story_v2-20260430-204325-9e5486df.csv"

rows = []
with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Total rows: {len(rows)}")
print()

# Inspect what columns have values for each row
for i, r in enumerate(rows, 1):
    populated = {k: v[:80] if isinstance(v, str) else v for k, v in r.items() if v not in (None, "", "None")}
    print(f"--- Row {i} ---")
    print(f"  status: {r.get('status')!r}")
    print(f"  error: {r.get('error')!r}")
    print(f"  latency: {r.get('latency')!r}")
    print(f"  tokens: {r.get('tokens')!r}")
    print(f"  f1_score: {r.get('f1_score')!r}")
    print(f"  clarity: {r.get('clarity')!r}")
    print(f"  precision: {r.get('precision')!r}")
    print(f"  feedback_key: {r.get('feedback_key')!r}")
    outs = r.get("outputs") or ""
    print(f"  outputs len: {len(outs)}")
