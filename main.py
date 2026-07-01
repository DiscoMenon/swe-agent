from langgraph.graph import StateGraph, END
from state import AgentState
from agents.fetcher import fetcher_node
from agents.explorer import explorer_node
from agents.planner import planner_node
from agents.coder import coder_node
from agents.pr_creator import pr_creator_node

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("fetcher", fetcher_node)
    graph.add_node("explorer", explorer_node)
    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("pr_creator", pr_creator_node)
    graph.add_edge("coder", "pr_creator")
    graph.add_edge("pr_creator", END)
    graph.add_edge("fetcher", "explorer")
    graph.add_edge("explorer", "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", END)
    graph.set_entry_point("fetcher")
    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({
        "issue_url": "https://github.com/DiscoMenon/flask/issues/1",
        "issue_title": "", "issue_body": "", "repo_owner": "", "repo_name": "",
        "relevant_files": [], "plan": None, "code_changes": None,
        "test_results": None, "pr_url": None, "error": None
    })
    
    print(f"Issue: {result['issue_title']}\n")
    print(f"Plan:\n{result['plan']}\n")
    print(f"Files changed: {list(result['code_changes'].keys()) if result['code_changes'] else 'None'}")
    if result['code_changes']:
        for filepath, diff in result['code_changes'].items():
            print(f"\n--- Diff for {filepath} ---")
            print(diff[:500])
    print(f"\nPR URL: {result.get('pr_url', 'Failed')}")
    print(f"Error: {result.get('error', 'None')}")