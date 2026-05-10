import yaml
with open("prompts/bug_to_user_story_v2.yml", encoding="utf-8") as f:
    data = yaml.safe_load(f)
sp = data["bug_to_user_story_v2"]["system_prompt"]
up = data["bug_to_user_story_v2"]["user_prompt"]
techs = data["bug_to_user_story_v2"]["techniques"]
print("YAML valid")
print(f"system_prompt: {len(sp)} chars / {sp.count(chr(10)) + 1} lines")
print(f"user_prompt:   {len(up)} chars / {up.count(chr(10)) + 1} lines")
print(f"techniques:    {techs}")
