"""Fetch outputs from the latest evaluation run for inspection."""
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
sys.stdout.reconfigure(encoding="utf-8")

from langsmith import Client

client = Client()
ds = list(client.list_datasets(dataset_name="prompt-optimization-challenge-resolved-eval"))[0]
projects = list(client.list_projects(reference_dataset_id=str(ds.id)))


def proj_time(p):
    for attr in ("start_time", "created_at", "modified_at"):
        v = getattr(p, attr, None)
        if v is not None:
            return v
    return None


projects = [p for p in projects if proj_time(p) is not None]
projects.sort(key=proj_time, reverse=True)

if not projects:
    print("No projects found")
    sys.exit(1)

proj = projects[0]
print(f"Latest project: {proj.name}")
print(f"Time: {proj_time(proj)}")
print()

runs = list(client.list_runs(project_name=proj.name, run_type="chain", limit=50))
if not runs:
    runs = list(client.list_runs(project_name=proj.name, limit=200))

print(f"Found {len(runs)} runs\n")

for r in runs:
    inp = r.inputs.get("bug_report", "") if r.inputs else ""
    out = r.outputs.get("output", "") if r.outputs else ""
    if not out:
        continue
    label = inp[:60].replace("\n", " ")
    print(f"=== {label}... ===")
    print(out)
    print()
    print("-" * 80)
    print()
