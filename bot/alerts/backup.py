import base64
import json
import urllib.error
import urllib.request

API = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "flex-monitoring-bot",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_remote(repo: str, path: str, branch: str, token: str) -> tuple[str | None, str | None]:
    """Return (content, sha) for the remote file, or (None, None) if it doesn't exist yet."""
    url = f"{API}/repos/{repo}/contents/{path}?ref={branch}"
    req = urllib.request.Request(url, headers=_headers(token), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise
    return base64.b64decode(data["content"]).decode(), data["sha"]


def put_remote(repo: str, path: str, branch: str, token: str, text: str, sha: str | None) -> str:
    """Write the file and return its new sha. Pass the previous sha (or None to create)."""
    body = {
        "message": "update alerts state",
        "content": base64.b64encode(text.encode()).decode(),
        "branch": branch,
    }
    if sha:
        body["sha"] = sha
    url = f"{API}/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=_headers(token), method="PUT")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read())["content"]["sha"]
