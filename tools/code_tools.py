import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def find_relevant_files(file_tree: list, issue_title: str, issue_body: str) -> list:
    file_list = "\n".join(file_tree)
    
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {
                "role": "user",
                "content": f"""Given this GitHub issue, return the 5-7 most relevant file paths from the list below.
                
Issue title: {issue_title}
Issue body: {issue_body}

File tree:
{file_list}

Return ONLY a JSON array of file paths, nothing else. Example: ["src/main.py", "src/utils.py"]"""
            }
        ]
    )
    
    import json
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)