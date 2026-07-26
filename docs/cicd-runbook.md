# CI/CD Operations Runbook

## Purpose

Operational guide for deploying, validating, swapping, and rolling back across DEV, STAGING, and PROD (Blue-Green) environments.

## Workflows

- Notebook deploy DEV: `.github/workflows/push-to-dev-refactored.yml`
- Notebook deploy STAGING: `.github/workflows/push-to-staging-refactored.yml`
- Notebook deploy PROD: `.github/workflows/push-to-prod-refactored.yml`
- Blue-Green swap: `.github/workflows/swap-blue-green-prod-env-refactored.yaml`
- Dashboard deploy: `.github/workflows/deploy-app-service.yml`

## Standard Deployment Flow

### DEV

1. Merge PR into `dev`.
2. Monitor workflow completion.
3. Verify Databricks health check and log ingestion.

### STAGING

1. Merge PR into `staging`.
2. Confirm workflow success and logs.

### PROD

1. Merge PR into `prod`.
2. Approve environment gate (`production`).
3. Confirm deployment, health checks, and smoke tests.

## Blue-Green Swap (Production)

1. Run workflow dispatch for `.github/workflows/swap-blue-green-prod-env-refactored.yaml`.
2. Keep `force_swap=false` unless emergency override is required.
3. Validate pre-checks and endpoint state changes.
4. Confirm release tag creation and Log Analytics event.

## Rollback Procedures

### Rollback: Blue-Green Swap

Use when production behavior degrades after swap.

1. Re-run swap workflow to flip traffic back to prior color.
2. Verify endpoint status and health checks.
3. Confirm service stability before closing incident.

### Rollback: Notebook Deploy

Use when notebook deployment introduces failures.

1. Revert offending commit on target branch.
2. Merge revert PR.
3. Confirm redeploy workflow succeeds.

### Rollback: Dashboard Deploy

1. On `prod`, redeploy previous known-good image tag to staging slot.
2. Swap slots back.
3. Run post-swap health check.

## Incident Response

### Sev-1 Criteria

- Production endpoint unavailable.
- Repeated health check failure post deployment.
- Swap verification failure with traffic impact.

### Immediate Actions

1. Freeze new merges to `prod`.
2. Trigger rollback path (prefer traffic swap rollback first).
3. Capture workflow run IDs and timestamps.
4. Notify stakeholders.

## Observability and Verification

Use KQL query sets in `.github/workflows/scripts/kql-queries.md` for:

- Deployment success rate and failure trends.
- Swap history and active environment analysis.
- Long-running deployments and anomalies.

## Secrets and Environment Governance

- Keep `production` secrets scoped to production environment.
- Enforce required reviewers on `production` environment approvals.
- Rotate PAT and cloud credentials on a regular schedule.

## On-Call Quick Commands

- Re-run failed workflow from GitHub UI.
- Trigger swap workflow dispatch manually.
- Validate YAML and workflow quality locally:
  - `~/.local/bin/pre-commit run --all-files`
  - `actionlint .github/workflows/*.yml .github/workflows/*.yaml`

## Post-Incident Checklist

1. Document root cause and timeline.
2. Add preventive checks (lint/test/health gate) if gap identified.
3. Update this runbook if process changed.
4. Link workflow run and remediation PR in incident notes.
