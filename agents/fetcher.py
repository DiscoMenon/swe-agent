from state import AgentState
from tools.github_tools import fetch_issue

def fetcher_node(state: AgentState) -> AgentState:
    result = fetch_issue(state["issue_url"])
    return {
        **state,
        "issue_title": result["title"],
        "issue_body": result["body"],
        "repo_owner": result["owner"],
        "repo_name": result["repo_name"]
    }