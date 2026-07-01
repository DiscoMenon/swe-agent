# Autonomous SWE Agent

A multi-node AI agent that autonomously resolves GitHub issues by reading the codebase, writing a fix, and opening a Pull Request. Built with LangGraph, it supports self-correction — if a generated diff fails validation, the agent replans and retries automatically.

## How it works

Seven nodes orchestrated in a loop:

1. **Fetcher** - Parses the GitHub issue URL and retrieves the issue title and description
2. **Explorer** - Fetches the repo file tree and uses an LLM to identify the most relevant files
3. **Planner** - Analyzes the issue and relevant code, produces a step-by-step fix plan
4. **Coder** - Implements the fix as unified diffs across the relevant files
5. **Validator** - Checks whether the generated diffs are valid and parseable
6. **Replanner** - If validation fails, rewrites the plan with the error as context and retries (up to 3x)
7. **PR Creator** - Creates a new branch, applies the diffs correctly, and opens a Pull Request

## Stack

- LangGraph for multi-node agent orchestration with conditional retry loop
- FastAPI + Server-Sent Events for real-time streaming web UI
- PyGithub for GitHub API integration
- `patch` library for correct unified diff application
- OpenRouter for LLM access
- Python 3.11

## Usage

### Web UI

```bash
pip install -r requirements.txt
cp .env.example .env
# add your GITHUB_TOKEN and OPENROUTER_API_KEY to .env
uvicorn server:app --reload
```

Open `http://localhost:8000`, paste a GitHub issue URL and watch the agent work in real time.

### CLI

```bash
python main.py --issue https://github.com/owner/repo/issues/123
```

## Example output

```
SWE Agent starting...
Issue: https://github.com/DiscoMenon/flask/issues/1

Issue: Improve --env-file flag description
Plan: 1. Update help text in cli.py ...
Files changed: ['src/flask/cli.py']
PR opened: https://github.com/DiscoMenon/flask/pull/2
```

## Project structure

```
swe-agent/
├── agents/
│   ├── fetcher.py       # GitHub issue fetching
│   ├── explorer.py      # LLM-based relevant file selection
│   ├── planner.py       # Fix planning
│   ├── coder.py         # Diff generation
│   ├── validator.py     # Diff validation
│   ├── replanner.py     # Self-correction replanning
│   └── pr_creator.py    # Branch creation + PR opening
├── tools/
│   ├── github_tools.py  # GitHub API helpers
│   └── code_tools.py    # LLM-based file ranking
├── frontend/
│   └── index.html       # Streaming web UI
├── state.py             # LangGraph shared state
├── server.py            # FastAPI backend
└── main.py              # CLI entrypoint
```