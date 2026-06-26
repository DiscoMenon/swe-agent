from langgraph.graph import StateGraph, END
from state import AgentState
from agents.fetcher import fetcher_node
from agents.explorer import explorer_node

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("fetcher", fetcher_node)
    graph.add_node("explorer", explorer_node)
    graph.add_edge("fetcher", "explorer")
    graph.add_edge("explorer", END)
    graph.set_entry_point("fetcher")
    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({
        "issue_url": "https://github.com/pallets/flask/issues/5551",
        "issue_title": "", "issue_body": "", "repo_owner": "", "repo_name": "",
        "relevant_files": [], "plan": None, "code_changes": None,
        "test_results": None, "pr_url": None, "error": None
    })
    
    print(f"Issue: {result['issue_title']}")
    print(f"Repo: {result['repo_owner']}/{result['repo_name']}")
    print(f"\nRelevant files found: {len(result['relevant_files'])}")
    for f in result['relevant_files']:
        print(f"  - {f['path']}")