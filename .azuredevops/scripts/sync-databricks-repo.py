import json
import os
import urllib.request

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
repo_url = os.environ["REPO_URL"]
repo_branch = os.environ["DATABRICKS_REPO_BRANCH"]
repo_provider = os.environ["DATABRICKS_REPO_PROVIDER"]
repo_name = os.environ["BUILD_REPOSITORY_NAME"].split("/")[-1]
repo_path = f"/Repos/CS-databricks-dev/{repo_name}"

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
existing = next((r for r in repos if r.get("url") == repo_url or r.get("path") == repo_path), None)

if existing is None:
    created = request_json(
        "/api/2.0/repos",
        method="POST",
        payload={
            "url": repo_url,
            "provider": repo_provider,
            "path": repo_path,
            "branch": repo_branch,
        },
    )
    repo_id = created["id"]
    print(f"Created Databricks repo id={repo_id} path={repo_path}")
else:
    repo_id = existing["id"]
    print(f"Databricks repo exists id={repo_id} path={existing.get('path')}")

request_json(
    f"/api/2.0/repos/{repo_id}",
    method="PATCH",
    payload={"branch": repo_branch},
)
print(f"Updated Databricks repo {repo_id} to branch {repo_branch}")
