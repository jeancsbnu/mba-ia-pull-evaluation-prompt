"""Dump full output and reference for a specific example from a CSV."""
import csv
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

path = sys.argv[1]
target_idx = int(sys.argv[2])

with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

row = rows[target_idx - 1]
inputs = json.loads(row.get("inputs", "{}"))
refs = json.loads(row.get("reference_outputs", "{}"))
outs = json.loads(row.get("outputs", "{}"))

print("=" * 80)
print(f"EXAMPLE {target_idx}")
print("=" * 80)
print("\n[BUG REPORT]\n")
print(inputs.get("bug_report", ""))
print("\n" + "-" * 80)
print("[OUTPUT]\n")
print(outs.get("output", ""))
print("\n" + "-" * 80)
print("[REFERENCE]\n")
print(refs.get("reference", ""))
