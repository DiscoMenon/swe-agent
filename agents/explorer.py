from state import AgentState
from tools.github_tools import fetch_file_tree, fetch_file_content
from tools.code_tools import find_relevant_files

def explorer_node(state: AgentState) -> AgentState:
    file_tree = fetch_file_tree(state["repo_owner"], state["repo_name"])
    relevant_paths = find_relevant_files(file_tree, state["issue_title"], state["issue_body"])
    
    relevant_files = []
    for path in relevant_paths:
        content = fetch_file_content(state["repo_owner"], state["repo_name"], path)
        if content:
            relevant_files.append({"path": path, "content": content[:3000]})
    
    return {**state, "relevant_files": relevant_files}