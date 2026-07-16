import json
import os
import urllib.error
import urllib.request

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
cluster_name = os.environ["DATABRICKS_CLUSTER_NAME"]
data_security_mode = os.environ.get("DATABRICKS_DATA_SECURITY_MODE", "USER_ISOLATION")
cluster_policy_id = os.environ.get("DATABRICKS_CLUSTER_POLICY_ID", "").strip()

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
    create_payload = {
        "cluster_name": cluster_name,
        "spark_version": spark_version,
        "node_type_id": node_type_id,
        "num_workers": 1,
        "autotermination_minutes": 30,
        # Many Azure Databricks workspaces disable NO_ISOLATION; USER_ISOLATION is broadly allowed.
        "data_security_mode": data_security_mode,
    }

    if cluster_policy_id:
        create_payload["policy_id"] = cluster_policy_id
        # If a policy enforces access mode, do not send a conflicting custom access mode.
        create_payload.pop("data_security_mode", None)

    def _create_with_payload(payload: dict) -> dict:
        return db_post("/api/2.0/clusters/create", payload)

    try:
        created = _create_with_payload(create_payload)
    except RuntimeError as err:
        err_text = str(err)
        if "FEATURE_DISABLED" not in err_text:
            raise

        # Workspaces with policy-enforced access modes may reject custom cluster creation.
        if not cluster_policy_id:
            policies = db_get("/api/2.0/policies/clusters/list").get("policies", [])
            if not policies:
                raise RuntimeError(
                    "Cluster creation is restricted by workspace policy and no cluster policies were found. "
                    "Set DATABRICKS_CLUSTER_POLICY_ID to an allowed policy id in Azure DevOps variable group "
                    "'databricks-dev'."
                ) from err

            selected_policy_id = policies[0].get("policy_id")
            if not selected_policy_id:
                raise RuntimeError(
                    "Cluster policies were returned but no usable policy_id was found. "
                    "Set DATABRICKS_CLUSTER_POLICY_ID explicitly."
                ) from err

            print(f"Retrying cluster create with policy_id={selected_policy_id}")
            create_payload["policy_id"] = selected_policy_id
            create_payload.pop("data_security_mode", None)
            created = _create_with_payload(create_payload)
        else:
            raise

    cluster_id = created["cluster_id"]
else:
    cluster_id = cluster["cluster_id"]
    state = cluster.get("state", "UNKNOWN")
    print(f"Cluster exists: {cluster_name} ({cluster_id}) state={state}")
    if state in {"TERMINATED", "TERMINATING", "ERROR"}:
        print(f"Starting cluster: {cluster_id}")
        db_post("/api/2.0/clusters/start", {"cluster_id": cluster_id})

print(f"Using cluster_id={cluster_id}")
