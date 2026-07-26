# Integration Testing Procedures

## Scope

This procedure validates the CI/CD system end-to-end for Databricks notebook deployments, App Service dashboard deployments, and Blue-Green production swaps.

## Preconditions

- GitHub Environments exist: `dev`, `staging`, `production`.
- Required repository/environment secrets are configured.
- Azure resources exist and are reachable (`countrystats-showcase` RG, ACR, App Service, Traffic Manager, Databricks workspaces).
- Branch protections and required checks are enabled.

## Test Matrix

| Flow                    | Trigger                     | Expected Outcome                                                             |
| ----------------------- | --------------------------- | ---------------------------------------------------------------------------- |
| DEV notebook deploy     | Merge PR into `dev`         | Notebooks deployed to DEV workspace, health check passes, log event sent     |
| STAGING notebook deploy | Merge PR into `staging`     | Notebooks deployed to Staging workspace, health check passes, log event sent |
| PROD notebook deploy    | Merge PR into `prod`        | Deployment waits for approval, deploys to target color, smoke tests pass     |
| Blue-Green swap         | Manual dispatch             | Standby color becomes active, verification passes, release created           |
| Dashboard deploy        | Push in `src/monitoring/**` | Image built/pushed, App Service slot deployed, prod swaps slots              |

## Test Data and Inputs

Use a deterministic, low-risk change set for each test:

- Notebook deployment change: small markdown/comment update in `src/notebooks/top_100_countries_population.ipynb`.
- Dashboard deployment change: non-functional text change in monitoring UI source.
- Swap test: no code change needed; use workflow dispatch.

## Procedure 1: DEV Deployment Validation

1. Create branch `feature/test-dev-deploy` from `dev`.
2. Commit a small notebook change.
3. Open PR to `dev`, merge.
4. Verify workflow `push-to-dev-refactored.yml` completed successfully.
5. Verify artifacts/logs:
   - `deployment-result.json` exists in logs/output step.
   - Health check reports workspace accessible.
6. Verify observability:
   - Log entry exists in Log Analytics for `environment=dev`.

Pass criteria:

- Workflow status is `success`.
- No notebook deployment failures.

## Procedure 2: STAGING Deployment Validation

1. Create branch from `staging`.
2. Commit a small notebook change.
3. Open PR to `staging`, merge.
4. Verify workflow `push-to-staging-refactored.yml` succeeded.
5. Confirm log event in Log Analytics for `environment=staging`.

Pass criteria:

- Workflow status is `success`.
- Health check passes.

## Procedure 3: PROD Deployment Validation

1. Create PR into `prod` with minimal notebook change.
2. Merge PR.
3. Approve production environment gate when prompted.
4. Verify workflow `push-to-prod-refactored.yml`:
   - Determine target env step outputs expected color.
   - Deploy step succeeds.
   - Health and smoke tests pass.

Pass criteria:

- Approved run completes `success`.
- Production log entry generated.

## Procedure 4: Blue-Green Swap Validation

1. Manually run `swap-blue-green-prod-env-refactored.yaml` (`workflow_dispatch`).
2. Keep `force_swap=false` for standard validation.
3. Verify:
   - Pre-swap checks run successfully.
   - Active endpoint disabled and standby enabled.
   - Post-swap verification passes.
   - Release is created.

Pass criteria:

- Workflow `success`.
- Active color toggled.

## Procedure 5: Dashboard Deploy Validation

1. Commit a minimal change under `src/monitoring/**` on `dev`, `staging`, and `prod` (separate runs).
2. Verify `deploy-app-service.yml`:
   - Node build and tests run.
   - Docker image is pushed.
   - Target slot deployment succeeds.
   - On `prod`, slot swap and post-swap health check succeed.

Pass criteria:

- Workflow `success` for each branch.
- Application responds from expected slot/environment.

## Failure Triage Checklist

1. Confirm secret availability and scope.
2. Confirm environment approval was granted for production jobs.
3. Inspect failing script output in workflow logs.
4. Correlate with Log Analytics events and timeline.
5. Re-run only after root-cause hypothesis is identified.

## Exit Criteria

Integration testing is complete when:

- All 5 procedures pass at least once.
- No unresolved high-severity failures remain.
- Runbook rollback path has been exercised successfully.
