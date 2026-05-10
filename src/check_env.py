import os, sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client

load_dotenv(Path(__file__).parent.parent / ".env")
sys.stdout.reconfigure(encoding='utf-8')

client = Client()

# Inspecionar runs do projeto principal buscando feedback
print("=== RUNS DO PROJETO 'evaluation-prompt' ===")
runs = list(client.list_runs(project_name="evaluation-prompt", limit=20))
print(f"Total de runs: {len(runs)}")

for r in runs[:5]:
    feedback = list(client.list_feedback(run_ids=[str(r.id)]))
    print(f"\n  run_id={str(r.id)[:8]} | type={r.run_type} | name={r.name}")
    print(f"  feedback: {len(feedback)} items")
    if feedback:
        for fb in feedback:
            print(f"    key={fb.key} score={fb.score}")
