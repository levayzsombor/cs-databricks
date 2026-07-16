import json
import os
import urllib.error
import urllib.request

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
cluster_name = os.environ["DATABRICKS_CLUSTER_NAME"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}


def _request(path: str, method: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(f"{host}{path}", headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code in (401, 403):
            raise RuntimeError(
                "Databricks authentication failed with "
                f"HTTP {exc.code} for host {host}. "
                "Ensure DATABRICKS_TOKEN was created in this exact workspace host "
                "and is still valid, then update variable group 'databricks-dev'. "
                f"API path: {path}. Response: {body}"
            ) from exc
        raise RuntimeError(
            f"Databricks API call failed with HTTP {exc.code} for {path}. Response: {body}"
        ) from exc


def db_get(path: str) -> dict:
    return _request(path, "GET")


def db_post(path: str, payload: dict) -> dict:
    return _request(path, "POST", payload)


spark_versions = db_get("/api/2.0/clusters/spark-versions").get("versions", [])
lts_spark = next((v.get("key") for v in spark_versions if v.get("long_term_support") and v.get("key")), None)
spark_version = lts_spark or (spark_versions[0].get("key") if spark_versions else None)
if not spark_version:
    raise RuntimeError("No Databricks Spark version could be discovered from /clusters/spark-versions")

node_types = db_get("/api/2.0/clusters/list-node-types").get("node_types", [])
available_node_types = [n.get("node_type_id") for n in node_types if n.get("node_type_id")]
if not available_node_types:
    raise RuntimeError("No Databricks node types could be discovered from /clusters/list-node-types")

preferred = ["Standard_DS3_v2", "Standard_D4s_v3", "Standard_D8s_v3"]
node_type_id = next((n for n in preferred if n in available_node_types), available_node_types[0])

clusters = db_get("/api/2.0/clusters/list").get("clusters", [])
cluster = next((c for c in clusters if c.get("cluster_name") == cluster_name), None)

if cluster is None:
    print(f"Creating cluster: {cluster_name}")
    created = db_post(
        "/api/2.0/clusters/create",
        {
            "cluster_name": cluster_name,
            "spark_version": spark_version,
            "node_type_id": node_type_id,
            "num_workers": 1,
            "autotermination_minutes": 30,
        },
    )
    cluster_id = created["cluster_id"]
else:
    cluster_id = cluster["cluster_id"]
    state = cluster.get("state", "UNKNOWN")
    print(f"Cluster exists: {cluster_name} ({cluster_id}) state={state}")
    if state in {"TERMINATED", "TERMINATING", "ERROR"}:
        print(f"Starting cluster: {cluster_id}")
        db_post("/api/2.0/clusters/start", {"cluster_id": cluster_id})

print(f"Using cluster_id={cluster_id}")
