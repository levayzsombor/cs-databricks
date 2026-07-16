import json
import os
import urllib.request
from typing import Any, cast

JsonDict = dict[str, Any]

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
repo_branch = os.environ["DATABRICKS_REPO_BRANCH"]
target_path = os.environ["DATABRICKS_WORKSPACE_REPO_PATH"]

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
target = next((r for r in repos if _string_value(r, "path") == target_path), None)

if target is None:
    raise RuntimeError(f"Databricks workspace repo path not found: {target_path}")

repo_id = _int_value(target, "id")
if repo_id is None:
    raise RuntimeError("Databricks workspace repo record did not include an integer id.")
request_json(
    f"/api/2.0/repos/{repo_id}",
    method="PATCH",
    payload={"branch": repo_branch},
)
print(f"Updated workspace repo {target_path} (id={repo_id}) to branch {repo_branch}")
