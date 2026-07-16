import json
import os
import re
import urllib.error
import urllib.request

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
cluster_name = os.environ["DATABRICKS_CLUSTER_NAME"]
data_security_mode = os.environ.get("DATABRICKS_DATA_SECURITY_MODE", "USER_ISOLATION")
cluster_policy_id = os.environ.get("DATABRICKS_CLUSTER_POLICY_ID", "").strip()
min_runtime = os.environ.get("DATABRICKS_MIN_RUNTIME", "13.3")
autoscale_min_workers = int(os.environ.get("DATABRICKS_AUTOSCALE_MIN_WORKERS", "1"))
autoscale_max_workers = int(os.environ.get("DATABRICKS_AUTOSCALE_MAX_WORKERS", "2"))
fixed_num_workers = int(os.environ.get("DATABRICKS_NUM_WORKERS", "1"))

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


def _runtime_tuple(version_key: str) -> tuple[int, int] | None:
    match = re.match(r"^(\d+)\.(\d+)", version_key)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _parse_min_runtime(value: str) -> tuple[int, int]:
    parsed = _runtime_tuple(value)
    if parsed is None:
        raise RuntimeError(f"Invalid DATABRICKS_MIN_RUNTIME format: {value}. Expected like '13.3'.")
    return parsed


def _policy_supports_min_runtime(policy: dict, minimum: tuple[int, int]) -> bool:
    definition_raw = policy.get("definition")
    if not definition_raw:
        return True

    try:
        definition = json.loads(definition_raw)
    except Exception:
        # If definition cannot be parsed, keep policy as candidate.
        return True

    spark = definition.get("spark_version")
    if not isinstance(spark, dict):
        return True

    if spark.get("type") == "fixed":
        value = spark.get("value")
        if isinstance(value, str):
            runtime = _runtime_tuple(value)
            if runtime is not None and runtime < minimum:
                return False
    return True


def _policy_priority(policy: dict) -> int:
    name = str(policy.get("name", "")).lower()
    if "shared compute" in name:
        return 0
    if "power user" in name:
        return 1
    if "personal compute" in name:
        return 2
    if "job compute" in name:
        return 3
    return 4


spark_versions = db_get("/api/2.0/clusters/spark-versions").get("versions", [])
min_runtime_tuple = _parse_min_runtime(min_runtime)

eligible_versions = []
for version in spark_versions:
    key = version.get("key")
    if not key:
        continue
    runtime = _runtime_tuple(key)
    if runtime is None:
        continue
    if runtime >= min_runtime_tuple:
        eligible_versions.append(version)

if not eligible_versions:
    raise RuntimeError(
        "No Databricks runtime meets minimum version "
        f"{min_runtime} in /clusters/spark-versions."
    )

lts_spark = next(
    (
        v.get("key")
        for v in eligible_versions
        if v.get("long_term_support") and v.get("key")
    ),
    None,
)
spark_version = lts_spark or eligible_versions[0].get("key")

node_types = db_get("/api/2.0/clusters/list-node-types").get("node_types", [])
available_node_types = [n.get("node_type_id") for n in node_types if n.get("node_type_id")]
if not available_node_types:
    raise RuntimeError(
        "No Databricks node types could be discovered from /clusters/list-node-types"
    )

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
        "autoscale": {
            "min_workers": autoscale_min_workers,
            "max_workers": autoscale_max_workers,
        },
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

    def _retry_worker_shape(err: RuntimeError, payload: dict) -> dict | None:
        err_text = str(err)

        if (
            "num_workers, the value cannot be present" in err_text
            and "autoscale.min_workers, the value must be present" in err_text
        ):
            adjusted = dict(payload)
            adjusted.pop("num_workers", None)
            adjusted["autoscale"] = {
                "min_workers": autoscale_min_workers,
                "max_workers": autoscale_max_workers,
            }
            print("Retrying cluster create with autoscale worker configuration")
            return _create_with_payload(adjusted)

        if (
            "autoscale.min_workers, the value cannot be present" in err_text
            or "num_workers, the value must be present" in err_text
        ):
            adjusted = dict(payload)
            adjusted.pop("autoscale", None)
            adjusted["num_workers"] = fixed_num_workers
            print("Retrying cluster create with fixed num_workers configuration")
            return _create_with_payload(adjusted)

        return None

    try:
        created = _create_with_payload(create_payload)
    except RuntimeError as err:
        worker_retry = _retry_worker_shape(err, create_payload)
        if worker_retry is not None:
            created = worker_retry
        else:
            err_text = str(err)
            if "FEATURE_DISABLED" not in err_text:
                raise

            if cluster_policy_id and "legacy access and legacy DBFS are disabled" in err_text:
                raise RuntimeError(
                    "Cluster policy "
                    f"{cluster_policy_id} appears to enforce an unsupported Databricks runtime. "
                    "Choose a policy compatible with runtime "
                    f"{min_runtime}+ (for example Shared Compute)."
                ) from err

            # Workspaces with policy-enforced access modes may reject custom cluster creation.
            if not cluster_policy_id:
                policies = db_get("/api/2.0/policies/clusters/list").get("policies", [])
                if not policies:
                    raise RuntimeError(
                        "Cluster creation is restricted by workspace policy and no "
                        "cluster policies were found. Set "
                        "DATABRICKS_CLUSTER_POLICY_ID to an allowed policy id in Azure "
                        "DevOps variable group "
                        "'databricks-dev'."
                    ) from err

                candidates = [
                    p
                    for p in policies
                    if p.get("policy_id")
                    and _policy_supports_min_runtime(p, min_runtime_tuple)
                ]
                if not candidates:
                    raise RuntimeError(
                        "No cluster policy in this workspace supports the minimum runtime "
                        f"{min_runtime}+. Set DATABRICKS_CLUSTER_POLICY_ID to a compatible policy."
                    ) from err

                candidates.sort(key=_policy_priority)
                created = None
                last_policy_error = None
                for policy in candidates:
                    selected_policy_id = policy.get("policy_id")
                    if not selected_policy_id:
                        continue

                    print(
                        "Retrying cluster create with policy_id="
                        f"{selected_policy_id} ({policy.get('name', 'unknown')})"
                    )
                    create_payload["policy_id"] = selected_policy_id
                    create_payload.pop("data_security_mode", None)

                    try:
                        created = _create_with_payload(create_payload)
                        break
                    except RuntimeError as policy_err:
                        retry_created = _retry_worker_shape(policy_err, create_payload)
                        if retry_created is not None:
                            created = retry_created
                            break
                        last_policy_error = policy_err
                        continue

                if created is None:
                    raise RuntimeError(
                        "Failed to create cluster with all compatible policies. "
                        f"Last error: {last_policy_error}"
                    ) from err
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
