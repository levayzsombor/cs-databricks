import json
import os
import urllib.request
from typing import Any, cast

JsonDict = dict[str, Any]

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


def request_json(path: str, method: str = "GET", payload: JsonDict | None = None) -> JsonDict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{host}{path}", headers=headers, data=data, method=method)
    with urllib.request.urlopen(req) as response:
        response_data = json.loads(response.read().decode("utf-8"))
        if not isinstance(response_data, dict):
            raise RuntimeError(f"Unexpected Databricks API response type for {path}.")
        return cast("JsonDict", response_data)


def _dict_list(value: object) -> list[JsonDict]:
    if not isinstance(value, list):
        return []
    items = cast("list[object]", value)
    return [cast("JsonDict", item) for item in items if isinstance(item, dict)]


def _string_value(item: JsonDict, key: str) -> str | None:
    value = item.get(key)
    return value if isinstance(value, str) else None


def _int_value(item: JsonDict, key: str) -> int | None:
    value = item.get(key)
    return value if isinstance(value, int) else None


repos = _dict_list(request_json("/api/2.0/repos?path_prefix=/Repos").get("repos", []))
existing = next(
    (r for r in repos if _string_value(r, "url") == repo_url or _string_value(r, "path") == repo_path),
    None,
)

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
    repo_id = _int_value(created, "id")
    if repo_id is None:
        raise RuntimeError("Databricks repo create response did not include an integer id.")
    print(f"Created Databricks repo id={repo_id} path={repo_path}")
else:
    repo_id = _int_value(existing, "id")
    if repo_id is None:
        raise RuntimeError("Existing Databricks repo record did not include an integer id.")
    print(f"Databricks repo exists id={repo_id} path={_string_value(existing, 'path')}")

request_json(
    f"/api/2.0/repos/{repo_id}",
    method="PATCH",
    payload={"branch": repo_branch},
)
print(f"Updated Databricks repo {repo_id} to branch {repo_branch}")
