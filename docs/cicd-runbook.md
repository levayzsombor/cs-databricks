# CI/CD Operations Runbook

## Purpose

Operational guide for deploying, validating, swapping, and rolling back across DEV, STAGING, and PROD (Blue-Green) environments.

## Workflows

- Notebook deploy DEV: `.github/workflows/push-to-dev-refactored.yml`
- Notebook deploy STAGING: `.github/workflows/push-to-staging-refactored.yml`
- Notebook deploy PROD: `.github/workflows/push-to-prod-refactored.yml`
- Blue-Green swap: `.github/workflows/swap-blue-green-prod-env-refactored.yaml`
- Dashboard deploy: `.github/workflows/deploy-app-service.yml`
- Pre-release creation: `.github/workflows/create-pre-release-scaffold.yml`

## Pre-Release Workflow Validation (2026-07-26)

### Scope

Validated `.github/workflows/create-pre-release-scaffold.yml` in two modes:

1. Dry-run path (`dry_run=true`)
2. Live-run path simulation (`dry_run=false`, local simulation without push/PR side effects)

### Evidence Artifacts

- `test_results/PRE_RELEASE_DRY_RUN_20260726T215533Z.txt`
- `test_results/PRE_RELEASE_LIVE_RUN_20260726T215536Z.txt`

### Results

1. **Dry-run validation: PASS**

- Input: `accepted_feature_tags=feature-test`, `version_bump=MINOR`
- Planned commits: `1`
- Baseline resolved and release notes generated successfully.

2. **Live-run simulation: FAIL (expected conflict surfaced)**

- Input: `accepted_feature_tags=feature-test`, `version_bump=MINOR`
- Cherry-pick failed on commit `0d6b93f08ea37bf9ae4e9a777f997347bad24f9a`
- Conflict file: `.devcontainer/devcontainer.json`
- This is a real merge conflict path in cherry-pick execution, not an empty-pick condition.

### Operational Interpretation

- Pre-release planning logic is functioning for dry-run.
- Non-dry-run path correctly fails closed on cherry-pick conflict.
- A conflict-resolution policy is required for operations before treating this workflow path as production-ready for all tag sets.

### GitHub-hosted Validation (Executed 2026-07-26)

Repository-hosted runs were executed on `milestone-3` with:

- `accepted_feature_tags=feature-test`
- `version_bump=MINOR`

1. Dry-run hosted run: **SUCCESS**

- Run ID: `30222160868`
- URL: `https://github.com/levayzsombor/cs-databricks/actions/runs/30222160868`
- Evidence: non-dry-run steps were skipped and `Dry-run completion marker` completed successfully.

2. Live-run hosted run: **FAILURE (cherry-pick conflict)**

- Run ID: `30222165987`
- URL: `https://github.com/levayzsombor/cs-databricks/actions/runs/30222165987`
- Failing step: `Create pre-release branch and cherry-pick commits (non-dry-run)`
- Conflict details from run logs:
  - `CONFLICT (content): Merge conflict in .devcontainer/devcontainer.json`
  - `error: could not apply 0d6b93f... added extension`

### Operational Conclusion

- Dry-run path is validated in GitHub-hosted execution.
- Live path is validated to fail closed on real cherry-pick conflict and requires conflict-resolution policy for production operations.

## Manual Conflict-Resolution Gate (Pre-Release)

The pre-release workflow now includes a dedicated manual gate job:

- Job: `manual-conflict-resolution-gate`
- Trigger condition: non-dry-run execution with detected cherry-pick conflict
- Environment: `pre-release-conflict-resolution`
- Behavior: requires environment approval, then exits with failure to enforce manual resolution before continuation

### Required Repository Configuration

1. Create/configure the `pre-release-conflict-resolution` environment in GitHub.
2. Add required reviewers for manual approval.
3. Optionally scope secrets to this environment if operational notifications are added later.

### Operator Procedure After Gate Fires

1. Check workflow summary for conflicting tag/commit and pre-release branch name.
2. Check out the pushed pre-release branch.
3. Resolve cherry-pick conflicts manually and push the branch.
4. Open/update PR to `staging`.
5. Re-run workflow only if automation should continue from a clean state.

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
