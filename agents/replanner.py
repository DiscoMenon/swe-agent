from state import AgentState
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def replanner_node(state: AgentState) -> AgentState:
    files_context = "\n\n".join([
        f"### {f['path']}\n{f['content']}"
        for f in state["relevant_files"]
    ])

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert software engineer. Your previous fix attempt failed.

Issue: {state['issue_title']}
Description: {state['issue_body']}

Previous plan:
{state['plan']}

Validation error:
{state['validation_error']}

Relevant code:
{files_context}

Write a revised fix plan that addresses the validation error. Be more specific about exact line numbers and changes needed."""
            }
        ]
    )

    return {
        **state,
        "plan": response.choices[0].message.content,
        "code_changes": None,
        "validation_error": None,
        "retry_count": state["retry_count"] + 1
    }