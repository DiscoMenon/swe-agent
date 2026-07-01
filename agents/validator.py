from state import AgentState
import patch as patch_lib
import io

def validator_node(state: AgentState) -> AgentState:
    if not state["code_changes"]:
        return {**state, "validation_error": "No code changes generated"}

    errors = []
    for filepath, diff in state["code_changes"].items():
        try:
            diff_bytes = diff.encode("utf-8")
            pset = patch_lib.PatchSet(io.BytesIO(diff_bytes))
            if not pset:
                errors.append(f"{filepath}: empty or unparseable diff")
        except Exception as e:
            errors.append(f"{filepath}: {str(e)}")

    if errors:
        return {**state, "validation_error": "\n".join(errors)}
    
    return {**state, "validation_error": None}