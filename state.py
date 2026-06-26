from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    issue_url: str
    issue_title: str
    issue_body: str
    repo_owner: str
    repo_name: str
    relevant_files: List[dict]  # [{"path": str, "content": str}]
    plan: Optional[str]
    code_changes: Optional[dict]  # {filepath: new_content}
    test_results: Optional[str]
    pr_url: Optional[str]
    error: Optional[str]