from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio, json
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END
from state import AgentState
from agents.fetcher import fetcher_node
from agents.explorer import explorer_node
from agents.planner import planner_node
from agents.coder import coder_node
from agents.validator import validator_node
from agents.replanner import replanner_node
from agents.pr_creator import pr_creator_node

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MAX_RETRIES = 3

def should_retry(state: AgentState) -> str:
    if state["validation_error"] and state["retry_count"] < MAX_RETRIES:
        return "replanner"
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

class IssueRequest(BaseModel):
    issue_url: str

def send(event: str, data: dict) -> str:
    return f"data: {json.dumps({'event': event, 'data': data})}\n\n"

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("frontend/index.html") as f:
        return f.read()

@app.post("/run")
async def run_agent(request: IssueRequest):
    async def stream():
        loop = asyncio.get_event_loop()
        agent = build_graph()

        initial_state = {
            "issue_url": request.issue_url,
            "issue_title": "", "issue_body": "",
            "repo_owner": "", "repo_name": "",
            "relevant_files": [], "plan": None,
            "code_changes": None, "validation_error": None,
            "retry_count": 0, "test_results": None,
            "pr_url": None, "error": None
        }

        yield send("status", {"message": "Fetching issue..."})
        await asyncio.sleep(0.1)

        result = await loop.run_in_executor(None, agent.invoke, initial_state)

        yield send("issue", {"title": result["issue_title"]})
        yield send("status", {"message": "Exploring codebase..."})
        yield send("files", {"files": [f["path"] for f in result["relevant_files"]]})
        yield send("status", {"message": "Planning fix..."})
        yield send("plan", {"plan": result["plan"]})
        yield send("status", {"message": "Writing code..."})
        yield send("changes", {"files": list(result["code_changes"].keys()) if result["code_changes"] else []})
        
        if result["retry_count"] > 0:
            yield send("retries", {"count": result["retry_count"]})

        if result["pr_url"]:
            yield send("pr", {"url": result["pr_url"]})
        if result["error"]:
            yield send("error", {"message": result["error"]})
        
        yield send("done", {})

    return StreamingResponse(stream(), media_type="text/event-stream")