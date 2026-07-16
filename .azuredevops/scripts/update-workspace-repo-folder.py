import json
import os
import urllib.request

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
repo_branch = os.environ["DATABRICKS_REPO_BRANCH"]
target_path = os.environ["DATABRICKS_WORKSPACE_REPO_PATH"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}


def request_json(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{host}{path}", headers=headers, data=data, method=method)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


repos = request_json("/api/2.0/repos?path_prefix=/Repos").get("repos", [])
target = next((r for r in repos if r.get("path") == target_path), None)

if target is None:
    raise RuntimeError(f"Databricks workspace repo path not found: {target_path}")

repo_id = target["id"]
request_json(
    f"/api/2.0/repos/{repo_id}",
    method="PATCH",
    payload={"branch": repo_branch},
)
print(f"Updated workspace repo {target_path} (id={repo_id}) to branch {repo_branch}")
