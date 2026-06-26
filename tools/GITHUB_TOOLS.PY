from github import Github
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

def parse_issue_url(url: str) -> tuple:
    parts = urlparse(url).path.strip("/").split("/")
    owner, repo, _, issue_number = parts[0], parts[1], parts[2], int(parts[3])
    return owner, repo, issue_number

def fetch_issue(url: str) -> dict:
    owner, repo_name, issue_number = parse_issue_url(url)
    repo = g.get_repo(f"{owner}/{repo_name}")
    issue = repo.get_issue(issue_number)
    return {
        "owner": owner,
        "repo_name": repo_name,
        "title": issue.title,
        "body": issue.body or ""
    }

def fetch_file_tree(owner: str, repo_name: str) -> list:
    repo = g.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_git_tree(sha="main", recursive=True)
    return [f.path for f in contents.tree if f.type == "blob" 
            and f.path.endswith((".py", ".js", ".ts", ".java", ".cpp", ".go"))]

def fetch_file_content(owner: str, repo_name: str, filepath: str) -> str:
    repo = g.get_repo(f"{owner}/{repo_name}")
    try:
        content = repo.get_contents(filepath)
        return content.decoded_content.decode("utf-8")
    except:
        return ""