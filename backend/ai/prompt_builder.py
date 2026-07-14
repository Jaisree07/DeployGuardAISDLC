import json

PROMPT_TEMPLATE = """You are a DevOps assistant. Explain the following deployment
regression pattern in plain English for a non-expert engineer. Be concise
(3-5 sentences), state what changed, why it matters, and one suggested
next step. Write prose, not a bulleted list of the raw numbers.

Pattern data:
{pattern_json}
"""


def build_prompt(pattern: dict) -> str:
    return PROMPT_TEMPLATE.format(pattern_json=json.dumps(pattern, indent=2))