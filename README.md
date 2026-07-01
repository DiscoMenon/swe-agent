# Autonomous SWE Agent

A multi-node AI agent that autonomously resolves GitHub issues by reading the codebase, writing a fix, and opening a Pull Request.

## How it works

1. **Fetcher** - Parses the GitHub issue URL and retrieves the issue title and description
2. **Explorer** - Fetches the repo file tree and uses an LLM to identify the most relevant files
3. **Planner** - Analyzes the issue and relevant code, produces a step-by-step fix plan
4. **Coder** - Implements the fix as unified diffs across the relevant files
5. **PR Creator** - Creates a new branch, commits the changes, and opens a Pull Request

## Stack

- LangGraph for multi-node agent orchestration
- PyGithub for GitHub API integration
- OpenRouter for LLM access
- Python 3.11

## Usage

```bash
pip install -r requirements.txt
cp .env.example .env
# add your GITHUB_TOKEN and OPENROUTER_API_KEY to .env
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
