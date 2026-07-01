from state import AgentState
from tools.github_tools import g
import patch as patch_lib
import io, tempfile, os, time

def apply_diff(original: str, diff: str) -> str:
    diff_bytes = diff.encode("utf-8")
    pset = patch_lib.PatchSet(io.BytesIO(diff_bytes))
    
    if not pset:
        return original
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(original)
        tmp_path = f.name
    
    try:
        pset.apply(root=os.path.dirname(tmp_path))
        with open(tmp_path, 'r', encoding='utf-8') as f:
            result = f.read()
        return result
    except Exception as e:
        print(f"Patch apply failed: {e}, falling back to original")
        return original
    finally:
        os.unlink(tmp_path)

def pr_creator_node(state: AgentState) -> AgentState:
    if not state["code_changes"]:
        return {**state, "error": "No code changes to commit"}

    try:
        repo = g.get_repo(f"{state['repo_owner']}/{state['repo_name']}")
        base = repo.get_branch("main")
        branch_name = f"swe-agent/fix-{int(time.time())}"

        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base.commit.sha
        )

        committed = False
        for filepath, diff in state["code_changes"].items():
            try:
                existing = repo.get_contents(filepath, ref="main")
                original = existing.decoded_content.decode("utf-8")
                updated = apply_diff(original, diff)
                repo.update_file(
                    path=filepath,
                    message=f"fix: {state['issue_title'][:50]}",
                    content=updated,
                    sha=existing.sha,
                    branch=branch_name
                )
                committed = True
            except Exception as e:
                print(f"Skipping {filepath}: {e}")
                continue

        if not committed:
            return {**state, "error": "No files could be committed"}

        pr = repo.create_pull(
            title=f"fix: {state['issue_title']}",
            body=f"Fixes #{state['issue_url'].split('/')[-1]}\n\n**Plan:**\n{state['plan']}",
            head=branch_name,
            base="main"
        )

        return {**state, "pr_url": pr.html_url}

    except Exception as e:
        return {**state, "error": str(e)}