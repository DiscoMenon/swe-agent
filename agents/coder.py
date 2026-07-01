from state import AgentState
from openai import OpenAI
import os, json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def coder_node(state: AgentState) -> AgentState:
    files_context = "\n\n".join([
        f"### {f['path']}\n{f['content']}" 
        for f in state["relevant_files"]
    ])

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert software engineer. Implement the fix for this GitHub issue.

Issue: {state['issue_title']}
Description: {state['issue_body']}

Plan:
{state['plan']}

Relevant code:
{files_context}

Return ONLY a JSON object where keys are file paths and values are unified diffs (like git diff output) showing exactly what to change. No full file contents, just the diffs.
Example format:
{{
  "src/flask/cli.py": "--- a/src/flask/cli.py\\n+++ b/src/flask/cli.py\\n@@ -10,7 +10,7 @@\\n context line\\n-old line\\n+new line\\n context line"
}}

Return ONLY valid JSON, no explanation, no markdown fences."""
            }
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        raw = raw[start:end]
        code_changes = json.loads(raw)
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw: {raw[:300]}")
        code_changes = {}

    return {**state, "code_changes": code_changes}