from state import AgentState
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def planner_node(state: AgentState) -> AgentState:
    files_context = "\n\n".join([
        f"### {f['path']}\n{f['content']}" 
        for f in state["relevant_files"]
    ])

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert software engineer. Analyze this GitHub issue and the relevant code, then create a clear fix plan.

Issue: {state['issue_title']}
Description: {state['issue_body']}

Relevant code:
{files_context}

Write a concise plan (3-5 steps) describing exactly what changes need to be made and in which files. Be specific about line numbers or function names where possible."""
            }
        ]
    )

    return {**state, "plan": response.choices[0].message.content}