# Log Analytics KQL Queries for Monitoring

This document contains 17 KQL queries for monitoring Databricks deployments and App Service health using Azure Log Analytics.

## Setup

These queries target the custom log table `DatabricksDeployment_CL` created by the `send-logs-to-analytics.py` script.

### Prerequisites

- Log Analytics Workspace: `7d0cb39c-348d-4863-91e1-efefc333fc11`
- Custom Log Table: `DatabricksDeployment_CL`

---

## Query 1: Deployment Success Rate (24h)

Monitor success/failure ratio across all environments.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(24h)
| summarize
    Total = count(),
    Success = count(status_s == "success"),
    Failed = count(status_s == "failed")
    by environment_s
| extend SuccessRate = (todouble(Success) / todouble(Total)) * 100
| project environment_s, Total, Success, Failed, SuccessRate
| sort by SuccessRate asc
```

---

## Query 2: Recent Deployments (7d)

List all deployments in the last 7 days with key details.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| project
    TimeGenerated,
    environment_s,
    status_s,
    branch_s,
    actor_s,
    commit_sha_s,
    workflow_run_number_s
| order by TimeGenerated desc
| limit 100
```

---

## Query 3: Blue-Green Swap History (30d)

Track all production Blue-Green swaps and their outcomes.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(30d) and environment_s == "prod"
| where status_s contains "swap"
| project
    TimeGenerated,
    status_s,
    workflow_run_id_s,
    actor_s,
    branch_s
| order by TimeGenerated desc
```

---

## Query 4: Production Environment Health

Show current BLUE/GREEN status and recent swaps.

```kusto
DatabricksDeployment_CL
| where environment_s in ("blue", "green")
| summarize
    LastDeployment = max(TimeGenerated),
    DeploymentCount = count(),
    SuccessCount = count(status_s == "success")
    by environment_s
| extend SuccessRate = (todouble(SuccessCount) / todouble(DeploymentCount)) * 100
| project environment_s, LastDeployment, DeploymentCount, SuccessRate
```

---

## Query 5: Databricks Job Execution Summary (24h)

Track scheduled job runs across environments.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(24h)
| where deployment_s contains "job"
| summarize
    JobCount = count(),
    SuccessfulRuns = count(status_s == "success"),
    FailedRuns = count(status_s == "failed")
    by environment_s
| extend SuccessRate = (todouble(SuccessfulRuns) / todouble(JobCount)) * 100
```

---

## Query 6: Failed Deployments (24h)

Find all failed deployments in the last 24 hours for quick remediation.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(24h)
| where status_s == "failed"
| project
    TimeGenerated,
    environment_s,
    branch_s,
    actor_s,
    workflow_run_id_s,
    workflow_run_number_s
| order by TimeGenerated desc
```

---

## Query 7: Deployment Duration Trends (30d)

Analyze deployment speed trends over 30 days.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(30d)
| summarize
    AvgDuration = avg(todouble(deployment_elapsed_seconds_d)),
    MaxDuration = max(todouble(deployment_elapsed_seconds_d)),
    MinDuration = min(todouble(deployment_elapsed_seconds_d)),
    Count = count()
    by bin(TimeGenerated, 1d), environment_s
| order by TimeGenerated desc
```

---

## Query 8: Notebook Deployment Success

Track individual notebook deployment success/failure.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| extend Notebooks = deployment_notebooks_deployed_s
| summarize
    Deployed = count(Notebooks contains "success"),
    Attempted = count()
    by environment_s, bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

---

## Query 9: App Service Dashboard Deployments

Monitor React dashboard deployments separately.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| where status_s contains "dashboard"
| summarize
    DeploymentCount = count(),
    SuccessCount = count(status_s == "dashboard_success")
    by environment_s, bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

---

## Query 10: Dashboard Health Status

Show current dashboard deployment health per environment.

```kusto
DatabricksDeployment_CL
| where status_s contains "dashboard"
| summarize
    LastDeployment = max(TimeGenerated),
    Status = any(status_s)
    by environment_s
| order by LastDeployment desc
```

---

## Query 11: Deployment Success Rate by Branch

Compare success rates across git branches.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(30d)
| summarize
    Total = count(),
    Success = count(status_s == "success")
    by branch_s
| extend SuccessRate = (todouble(Success) / todouble(Total)) * 100
| order by SuccessRate asc
```

---

## Query 12: Longest Running Deployments

Identify deployments that took longer than expected.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| project
    TimeGenerated,
    environment_s,
    status_s,
    deployment_elapsed_seconds_d,
    actor_s
| where deployment_elapsed_seconds_d > 300  // > 5 minutes
| order by deployment_elapsed_seconds_d desc
| limit 20
```

---

## Query 13: Anomaly Detection (Unusual Patterns)

Flag unusual deployment patterns (failures, delays, etc.).

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(24h)
| summarize
    FailureRate = count(status_s == "failed") * 100.0 / count(),
    AvgDuration = avg(todouble(deployment_elapsed_seconds_d)),
    Count = count()
    by environment_s
| where FailureRate > 10 or AvgDuration > 600
| project environment_s, FailureRate, AvgDuration
```

---

## Query 14: Service Uptime Report (7d)

Calculate uptime percentage by environment.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| summarize
    TotalChecks = count(),
    HealthyChecks = count(status_s == "success")
    by environment_s
| extend Uptime = (todouble(HealthyChecks) / todouble(TotalChecks)) * 100
| project environment_s, TotalChecks, HealthyChecks, Uptime
| order by Uptime asc
```

---

## Query 15: Deployment by Actor

See which team members are deploying and their success rates.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(30d)
| summarize
    TotalDeployments = count(),
    SuccessfulDeployments = count(status_s == "success")
    by actor_s
| extend SuccessRate = (todouble(SuccessfulDeployments) / todouble(TotalDeployments)) * 100
| order by SuccessRate asc
```

---

## Query 16: Deployment Frequency by Hour

Analyze when deployments typically occur.

```kusto
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| extend Hour = hour(TimeGenerated)
| summarize DeploymentCount = count() by Hour, environment_s
| order by Hour asc
```

---

## Query 17: Critical Failures (Extended Drill-Down)

Deep investigation of failed deployments with full context.

```kusto
DatabricksDeployment_CL
| where status_s == "failed" and TimeGenerated > ago(24h)
| project
    TimeGenerated,
    environment_s,
    branch_s,
    actor_s,
    commit_sha_s,
    workflow_run_id_s,
    repository_s,
    deployment_failures_s
| order by TimeGenerated desc
```

---

## Alert Configuration

### Recommended Alerts

1. **High Failure Rate**: Alert if failure rate > 20% in any environment
2. **Production Swap Anomaly**: Alert if unexpected Blue-Green swap occurs
3. **Deployment Timeout**: Alert if deployment takes > 10 minutes
4. **Dashboard Deployment Failed**: Alert if dashboard deployment fails
5. **No Deployments**: Alert if no deployments in 24h (possible automation failure)

### Alert Actions

- **Critical**: Notify on-call engineer via SMS/PagerDuty
- **High**: Send Slack notification to #deployments channel
- **Medium**: Create Azure DevOps work item
- **Low**: Store in Log Analytics for trend analysis

---

## Exporting Results

### For Dashboards

```kusto
// This query is designed for visualization
DatabricksDeployment_CL
| summarize
    Success = count(status_s == "success"),
    Failed = count(status_s == "failed")
    by bin(TimeGenerated, 1h), environment_s
| render barchart
```

### For Reports

```kusto
// Weekly summary for stakeholders
DatabricksDeployment_CL
| where TimeGenerated > ago(7d)
| summarize
    Deployments = count(),
    SuccessRate = count(status_s == "success") * 100.0 / count(),
    AvgDuration = avg(todouble(deployment_elapsed_seconds_d))
    by environment_s, week=startofweek(TimeGenerated)
| order by week desc
```

---

## Documentation

For more information:

- [Azure Log Analytics KQL Documentation](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
- [Databricks Deployment Guide](../../README.md)
- [Monitoring Strategy](./MONITORING.md)
