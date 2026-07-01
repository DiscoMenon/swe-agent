from state import AgentState
from tools.github_tools import g
import re

def apply_diff_simple(original: str, diff: str) -> str:
    lines = original.splitlines(keepends=True)
    result = lines.copy()
    
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            result.append(line[1:] + "\n")
    return "".join(result)

def pr_creator_node(state: AgentState) -> AgentState:
    if not state["code_changes"]:
        return {**state, "error": "No code changes to commit"}

    try:
        repo = g.get_repo(f"{state['repo_owner']}/{state['repo_name']}")
        
        # create a new branch
        base = repo.get_branch("main")
        branch_name = f"swe-agent/fix-issue"
        
        try:
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base.commit.sha
            )
        except Exception:
            branch_name = f"swe-agent/fix-issue-2"
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base.commit.sha
            )

        # commit each changed file
        for filepath, diff in state["code_changes"].items():
            try:
                existing = repo.get_contents(filepath, ref=branch_name)
                original = existing.decoded_content.decode("utf-8")
                updated = apply_diff_simple(original, diff)
                repo.update_file(
                    path=filepath,
                    message=f"fix: {state['issue_title'][:50]}",
                    content=updated,
                    sha=existing.sha,
                    branch=branch_name
                )
            except Exception as e:
                print(f"Skipping {filepath}: {e}")
                continue

        # open the PR
        pr = repo.create_pull(
            title=f"fix: {state['issue_title']}",
            body=f"Fixes #{state['issue_url'].split('/')[-1]}\n\n**Plan:**\n{state['plan']}",
            head=branch_name,
            base="main"
        )

        return {**state, "pr_url": pr.html_url}

    except Exception as e:
        return {**state, "error": str(e)}