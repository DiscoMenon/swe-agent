import argparse
from langgraph.graph import StateGraph, END
from state import AgentState
from agents.fetcher import fetcher_node
from agents.explorer import explorer_node
from agents.planner import planner_node
from agents.coder import coder_node
from agents.validator import validator_node
from agents.replanner import replanner_node
from agents.pr_creator import pr_creator_node
from dotenv import load_dotenv

load_dotenv()

MAX_RETRIES = 3

def should_retry(state: AgentState) -> str:
    if state["validation_error"] and state["retry_count"] < MAX_RETRIES:
        return "replanner"
    elif state["validation_error"]:
        return "pr_creator"  # give up, try anyway
    return "pr_creator"

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("fetcher", fetcher_node)
    graph.add_node("explorer", explorer_node)
    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("validator", validator_node)
    graph.add_node("replanner", replanner_node)
    graph.add_node("pr_creator", pr_creator_node)

    graph.add_edge("fetcher", "explorer")
    graph.add_edge("explorer", "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "validator")
    graph.add_conditional_edges("validator", should_retry)
    graph.add_edge("replanner", "coder")
    graph.add_edge("pr_creator", END)
    graph.set_entry_point("fetcher")
    return graph.compile()

def run(issue_url: str):
    app = build_graph()

    print(f"\nSWE Agent starting...")
    print(f"Issue: {issue_url}\n")

    result = app.invoke({
        "issue_url": issue_url,
        "issue_title": "", "issue_body": "",
        "repo_owner": "", "repo_name": "",
        "relevant_files": [], "plan": None,
        "code_changes": None, "validation_error": None,
        "retry_count": 0, "test_results": None,
        "pr_url": None, "error": None
    })

    print(f"Issue: {result['issue_title']}")
    print(f"\nPlan:\n{result['plan']}")
    print(f"\nRetries: {result['retry_count']}")
    print(f"\nFiles changed: {list(result['code_changes'].keys()) if result['code_changes'] else 'None'}")

    if result['pr_url']:
        print(f"\nPR opened: {result['pr_url']}")
    if result['error']:
        print(f"\nError: {result['error']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous SWE Agent")
    parser.add_argument("--issue", required=True, help="GitHub issue URL")
    args = parser.parse_args()
    run(args.issue)