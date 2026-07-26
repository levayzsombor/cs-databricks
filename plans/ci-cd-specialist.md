# CI/CD Specialist Agent - Implementation Plan

**Agent**: CI/CD Specialist Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 1 (Foundation) & 4 (Orchestration & Deployment)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Build and maintain CI/CD pipelines, GitHub Actions workflows, Helm charts, and Blue-Green deployment orchestration for Databricks environment management across 5 environments (DEV, UA, Staging, Prod Blue, Prod Green).

**Key Instructions to Follow**:

- github-actions-ci-cd-best-practices.instructions.md
- kubernetes-deployment-best-practices.instructions.md
- azure-verified-modules-terraform.instructions.md
- databricks-orchestration.instructions.md
- shell.instructions.md

---

## Status Matrix (Current)

| Area                                  | Status                                     | Evidence in Repository                                                                                                                                                                                              | Remaining Work                                                               |
| ------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Workflow refactor + script extraction | ✅ Completed                               | `.github/workflows/push-to-*.yml`, `.github/workflows/swap-blue-green-prod-env-refactored.yaml`, `.github/workflows/scripts/ci_*.sh`                                                                                | Keep script interfaces stable and documented                                 |
| Workflow lint validity                | ✅ Completed                               | `actionlint` clean on workflow set                                                                                                                                                                                  | Keep green after each workflow change                                        |
| Workflow token permissions hardening  | ✅ Completed                               | `permissions` added to all active workflows                                                                                                                                                                         | Periodically tighten per-step if scopes can be reduced                       |
| App Service dashboard deploy pipeline | ✅ Completed                               | `.github/workflows/deploy-app-service.yml`                                                                                                                                                                          | Optional: remove tolerant test/lint behavior (`                              |     | true`) when frontend stabilizes |
| Blue-Green manual swap workflow       | 🟨 Partial                                 | `.github/workflows/swap-blue-green-prod-env-refactored.yaml`                                                                                                                                                        | Finalize governance around production approvals and rollback drills          |
| Pre-release cherry-pick orchestration | ✅ Implemented with manual resolution gate | `.github/workflows/create-pre-release-scaffold.yml`, `test_results/PRE_RELEASE_DRY_RUN_20260726T215533Z.txt`, `test_results/PRE_RELEASE_LIVE_RUN_20260726T215536Z.txt`, hosted runs `30222160868` and `30222165987` | Validate gate behavior in a fresh hosted run and finalize edge-case handling |
| Helm environment coverage             | 🟨 Partial                                 | `helm/app-service`, `helm/databricks-jobs`                                                                                                                                                                          | Verify full DEV/UA/Staging/Prod values strategy and run `helm lint` gates    |
| Log Analytics operational readiness   | 🟨 Partial                                 | `ci_send_logs.sh`, `send-logs-to-analytics.py`, `kql-queries.md`                                                                                                                                                    | Add infra automation/validation for alerts + workspace setup                 |

---

## Completed Work

1. Refactored main deployment workflows to reusable shell scripts.
2. Added shell safety and argument validation in CI helper scripts.
3. Fixed YAML and shell lint issues across active CI/CD files.
4. Added explicit least-privilege `permissions` blocks to workflow files.
5. Added pre-release workflow with deterministic commit planning, cherry-pick execution, conflict reporting, and generated release notes.

---

## In-Progress Work

### Task 4.2: Pre-Release Cherry-Pick Automation

**Current state**: core automation implemented and lint-clean; hosted validation completed with expected dry-run success and live-run cherry-pick conflict.

**Implemented now**:

- Manual trigger with `accepted_feature_tags`, `version_bump`, `dry_run`
- Baseline selection from oldest non-accepted feature tag
- Deterministic commit ordering across `feature-*`, `hotfix-*`, and `version-*` tags
- Cherry-pick execution with conflict summary on failure
- Release-note generation and PR body enrichment
- Optional branch push and PR creation to `staging`
- Local dry-run and live-run simulation executed and documented in `docs/cicd-runbook.md`

**Still required**:

1. Validate manual gate behavior in a fresh hosted run after workflow update.
2. Add automated fallback/notification strategy for cherry-pick conflicts.
3. Finalize how merged-feature tags and alpha-version tags are linked post-merge.
4. Add regression checks for edge cases (missing tags, duplicate commits, empty plan).

---

## Next Actions (Priority Ordered)

1. Run end-to-end dry-run/live validation for pre-release workflow.
2. Add post-merge staging alpha tag + merged-feature tag automation linkage.
3. Add workflow tests/checks for the pre-release path (`dry_run` and real modes).
4. Validate Helm charts with explicit lint/deploy checks and capture outputs in docs.
5. Add/update runbook with operational playbooks for swap rollback and pre-release conflicts.

---

## Dependencies and Blockers

**External dependencies**:

- Azure subscription resources and operational access
- Monitoring UI integration for trigger/approval UX
- Repository governance decisions on approval policies

**Current blockers**:

- No hard technical blocker for scaffold completion.
- Production-ready pre-release orchestration depends on agreed conflict policy and approval process.

---

## Progress Log

### 2026-07-26

- Verified workflow syntax and lint status with `actionlint`.
- Consolidated workflow shell logic into `.github/workflows/scripts/ci_*.sh`.
- Added least-privilege permissions to active workflows.
- Added pre-release scaffold workflow: `.github/workflows/create-pre-release-scaffold.yml`.
- Updated CI/CD plan to reflect real completion state (completed vs partial vs pending).
- Productionized pre-release workflow internals (deterministic planning, cherry-pick, conflict summary, release notes).
- Configured devcontainer persistent auth mounts/env forwarding for gh, git, az, and databricks CLIs.
- Added startup auth-check helper script: `.devcontainer/post-start-auth-check.sh`.
- Ran local validation for pre-release workflow dry-run and live-run simulation.
- Dry-run result: pass (`test_results/PRE_RELEASE_DRY_RUN_20260726T215533Z.txt`).
- Live-run simulation result: cherry-pick conflict on `.devcontainer/devcontainer.json` for commit `0d6b93f08ea37bf9ae4e9a777f997347bad24f9a` (`test_results/PRE_RELEASE_LIVE_RUN_20260726T215536Z.txt`).
- Documented evidence and follow-up commands in `docs/cicd-runbook.md`.
- Executed GitHub-hosted dry-run validation: run `30222160868` (success).
- Executed GitHub-hosted live-run validation: run `30222165987` (failure at cherry-pick step due conflict in `.devcontainer/devcontainer.json`).
- Updated runbook with hosted run URLs and failure log evidence.
- Implemented manual conflict-resolution gate in `.github/workflows/create-pre-release-scaffold.yml` using environment `pre-release-conflict-resolution`.
- Updated workflow to suppress auto-PR creation when conflicts are detected and emit conflict outputs for gate handling.
- Updated runbook with manual gate setup and operator resolution procedure.

---

## Handoff Checklist

- [x] GitHub Actions workflows verified and enhanced
- [ ] Helm charts validated for full 5-environment strategy
- [ ] Azure Log Analytics fully validated with alerts and operational checks
- [x] Blue-Green deployment workflow implemented (manual swap path)
- [ ] Blue-Green approval + rollback drills documented and verified with operations
- [x] Pre-release automation scaffold created
- [x] Pre-release automation productionized (full cherry-pick + release-note logic)
- [x] Pre-release workflow validated with live repository runs
- [ ] End-to-end CI/CD rehearsal completed and documented

**When each item changes**: update this file on the same day with a new entry under "Progress Log".
