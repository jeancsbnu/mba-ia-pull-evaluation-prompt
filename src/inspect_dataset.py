import json, sys
sys.stdout.reconfigure(encoding='utf-8')

examples = [json.loads(l) for l in open('datasets/bug_to_user_story.jsonl', 'r', encoding='utf-8') if l.strip()]

# Mostrar referencias completas de TODOS os 10 primeiros para entender o padrao
for i in range(10):
    bug = examples[i]['inputs'].get('bug_report', '')
    ref = examples[i]['outputs'].get('reference', '')
    print(f'=== Ex {i+1} | BUG: {bug[:80]} ===')
    print(ref)
    print()
