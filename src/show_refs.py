import json, sys
sys.stdout.reconfigure(encoding='utf-8')
examples=[json.loads(l) for l in open('datasets/bug_to_user_story.jsonl','r',encoding='utf-8') if l.strip()]
for i in [12,13,14]:
    ref = examples[i]['outputs']['reference']
    print(f'=== Example {i+1} (full) ===')
    print(ref)
    print()
