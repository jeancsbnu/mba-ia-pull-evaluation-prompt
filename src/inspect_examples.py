import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
from langsmith import Client

client = Client()
project_name = os.getenv("LANGCHAIN_PROJECT", "prompt-optimization-challenge-resolved")
dataset_name = f"{project_name}-eval"

all_examples = list(client.list_examples(dataset_name=dataset_name))
examples = [e for e in all_examples
            if isinstance(e.inputs, dict) and "bug_report" in e.inputs
            and isinstance(e.outputs, dict) and e.outputs.get("reference")]
print(f"Total: {len(all_examples)}, com bug_report+reference: {len(examples)}")

for i, e in enumerate(examples[:10], 1):
    bug = e.inputs.get("bug_report", "")[:250]
    ref = (e.outputs.get("reference", "")[:200] if isinstance(e.outputs, dict) else "")
    print(f"\n--- Ex {i} ---")
    print(f"BUG: {bug}")
    print(f"REF: {ref}")
