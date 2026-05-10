import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
sys.stdout.reconfigure(encoding="utf-8")

from langsmith import Client

client = Client()
ds = list(client.list_datasets(dataset_name="prompt-optimization-challenge-resolved-eval"))[0]
projects = list(client.list_projects(reference_dataset_id=str(ds.id)))
print("Total projects:", len(projects))


def t(p):
    return getattr(p, "start_time", None) or getattr(p, "modified_at", None)


projects.sort(key=lambda p: t(p) or "", reverse=True)
for p in projects[:15]:
    print(p.name, "|", t(p))
