"""Run current prompt on specific examples and print output vs reference."""
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
sys.stdout.reconfigure(encoding="utf-8")

from langsmith import Client
from langchain.prompts import ChatPromptTemplate
from utils import get_llm
from langchain import hub

client = Client()
ds_name = "prompt-optimization-challenge-resolved-eval"
all_examples = list(client.list_examples(dataset_name=ds_name))

examples = [e for e in all_examples
            if isinstance(e.inputs, dict) and "bug_report" in e.inputs
            and isinstance(e.outputs, dict) and e.outputs.get("reference")]

prompt_template = hub.pull("bug_to_user_story_v2")
llm = get_llm()
chain = prompt_template | llm

# Ex 9 e Ex 1, 2, 3
target_indices = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [9]

for idx in target_indices:
    if idx < 1 or idx > len(examples):
        print(f"Ex {idx} fora do range")
        continue
    ex = examples[idx - 1]
    bug = ex.inputs.get("bug_report", "")
    ref = ex.outputs.get("reference", "")

    print("=" * 80)
    print(f"EX {idx}")
    print("=" * 80)
    print("\n[BUG REPORT]")
    print(bug)

    print("\n[OUTPUT ATUAL]")
    response = chain.invoke({"bug_report": bug})
    print(response.content)

    print("\n[REFERÊNCIA]")
    print(ref)
    print()
