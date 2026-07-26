---
description: 'Orchestration and automation workflows for Databricks environments, including pre-release branch creation, Blue-Green deployments, and tag-based environment management'
applyTo: '.azuredevops/**/*.yml, .azuredevops/**/*.yaml, .github/workflows/*.yml'
---

# Databricks Orchestration Workflows

Guidelines for designing and implementing automated orchestration workflows that manage Databricks environments, deployment pipelines, and version lifecycle.

## Core Concepts

### Version Lifecycle

The repository uses a structured version lifecycle:

1. **Dev Branch** → feature-_, hotfix-_, dev-version-update tags
2. **Staging Branch** → alpha-version-* tags
3. **Prod Branch** → version-* tags (semantic versioning X.X.X)

Each environment corresponds to a branch and version:

- **DEV Environment**: Latest dev branch code (auto-updated)
- **UA Environment**: Latest dev branch code (manual trigger)
- **Staging Environment**: Latest staging branch with alpha-version tag (auto-updated)
- **Prod (Blue)**: Active production version
- **Prod (Green)**: Inactive production version (updated before swap)

### Design Decisions

- **Pre-release cherry-picking**: Manually triggered (not automatic)
- **Blue-Green swap**: Requires manual approval before switching
- **Tag display on Monitoring page**: Only unaccepted feature tags (feature-* without merged-feature-* counterpart)
- **Data sources**:
  - REST Countries API: https://restcountries.com/
  - World Bank Developer API: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information

## Workflow Types

### 1. Pre-Release Creation Workflow (Manual Trigger)

**Purpose**: Create a pre-release branch with cherry-picked accepted features

**Trigger**: Manual button/API call (in Monitoring web page)

**Logic**:

1. Identify all accepted features (feature-* tags that have corresponding merged-feature-* tags)
2. Find the last commit before the oldest non-accepted feature tag (this is the baseline)
3. Cherry-pick all:
   - Accepted feature commits (from feature-* tags)
   - All hotfix commits (from hotfix-* tags since baseline)
   - All version commits (from version-* tags since baseline)
4. Create pre-release branch from dev
5. Open PR to staging with:
   - Title: "Pre-release: [list of features]"
   - Body: List all feature tags, hotfix tags, version tags
   - Label: MAJOR/MINOR/PATCH (manual selection)
6. Workflow ends; PR awaits review

**Pseudo-code**:

```
TRIGGER: Manual (e.g., via GitHub API call from Monitoring page)

INPUT: acceptance_status (which feature tags are accepted)

1. Get all commits on dev with tags
2. Find oldest non-accepted feature tag
3. Get commit before that tag (baseline)
4. Collect all commits since baseline with:
   - feature-* tag (must be in accepted list)
   - hotfix-* tag
   - version-* tag
5. Create new branch from dev: pre-release
6. Cherry-pick collected commits into pre-release
7. Create PR: pre-release → staging
   - Title with feature list
   - Labels: [MAJOR|MINOR|PATCH]
8. Post comment: "Cherry-picked X features, Y hotfixes, Z versions"
```

### 2. Staging Merge Workflow (Auto-Triggered on PR Merge)

**Purpose**: Update tags when code merges to staging

**Trigger**: PR merged to staging branch

**Logic**:

1. Determine version increment (MAJOR/MINOR/PATCH from PR label)
2. Get last alpha-version-* tag
3. Parse version (e.g., alpha-version-1.2.3)
4. Increment appropriately: 1.2.3 → 1.3.0 (MINOR)
5. Create new alpha-version-X.X.X tag at merge commit
6. Find all feature-* tags in the merge
7. Replace feature-* with merged-feature-* to mark as accepted
8. Log: "Merged to staging: alpha-version-2.1.0, accepted features: feature-auth, feature-reports"

**Pseudo-code**:

```
TRIGGER: PR merge to staging branch

1. Get PR labels to find MAJOR|MINOR|PATCH
2. Fetch latest alpha-version-* tag
3. Parse semantic version from tag
4. Increment version:
   - MAJOR: X+1.0.0
   - MINOR: X.Y+1.0
   - PATCH: X.Y.Z+1
5. Create tag: alpha-version-X.X.X at merge commit
6. For each feature-* tag in merge:
   - Create merged-feature-* tag at same commit
   - Tag indicates feature was accepted and merged
7. Push tags to repository
```

### 3. Production Merge Workflow (Auto-Triggered on PR Merge)

**Purpose**: Update tags when code merges to prod

**Trigger**: PR merged to prod branch

**Logic**:

1. Get latest alpha-version-* tag from staging
2. Extract version (e.g., alpha-version-2.1.5)
3. Create version-* tag (remove alpha- prefix): version-2.1.5
4. Trigger Blue-Green update:
   - Update inactive Prod environment with new version
   - Set flag: "Prod (Green) ready for swap review"
5. Log: "Production deployed: version-2.1.5, waiting for Blue-Green swap approval"

**Pseudo-code**:

```
TRIGGER: PR merge to prod branch

1. Get latest alpha-version-* tag from staging
2. Extract version X.X.X
3. Create tag: version-X.X.X at merge commit
4. Trigger infrastructure update:
   - Identify inactive Prod environment (Green)
   - Deploy version-X.X.X to Prod (Green)
   - Notify: "New version ready, waiting for swap approval"
5. Push tag to repository
```

### 4. Blue-Green Swap Workflow (Manual Approval)

**Purpose**: Switch active/inactive Prod environments

**Trigger**: Manual approval (e.g., via Monitoring page UI)

**Logic**:

1. Verify inactive Prod environment is healthy (health checks pass)
2. Update load balancer/traffic manager to route to inactive environment
3. Log switch:
   - Old active version (e.g., version-2.0.5)
   - New active version (e.g., version-2.1.5)
   - Timestamp
4. Update Monitoring page to show new active version
5. If rollback requested: reverse the traffic routing (keep both versions running)

**Pseudo-code**:

```
TRIGGER: Manual approval (e.g., HTTP endpoint called from Monitoring page)

INPUT: approval_token, swap_direction (active→green or active→blue)

1. Validate approval token
2. Run health checks on target environment:
   - Databricks cluster health
   - Data pipeline status
   - Connectivity to data sources
3. If health checks fail: abort, log error, notify stakeholders
4. Update load balancer configuration:
   - Old active traffic → goes to blue
   - Green (new) traffic → becomes active
5. Update Monitoring page state:
   - active_version = new version
   - inactive_version = old version
6. Log swap event with versions and timestamp
7. Notify stakeholders: "Blue-Green swap completed successfully"
```

### 5. Dev-Version-Update Workflow (Auto-Triggered on Prod Merge)

**Purpose**: Sync production version back to dev branch

**Trigger**: PR merged to prod branch (after version tag created)

**Logic**:

1. Get latest version-* tag created on prod
2. Create dev-version-update branch from dev
3. Update version file or marker (e.g., pyproject.toml version field)
4. Create PR: dev-version-update → dev
5. Merge PR with dev-version-* tag
6. This ensures dev branch knows about the version released to production

**Pseudo-code**:

```
TRIGGER: Auto-triggered after version-* tag created on prod

INPUT: latest_version (e.g., 2.1.5)

1. Create branch: dev-version-update-2.1.5
2. Update src/version.py or pyproject.toml:
   - version = "2.1.5"
3. Create PR: dev-version-update-2.1.5 → dev
   - Title: "Dev: Sync version 2.1.5 from production"
   - Body: Lists version history
4. Auto-merge PR (or wait for review)
5. Create tag: dev-version-2.1.5 at merge commit
```

## Tag Naming Conventions

| Tag Pattern        | Created By                      | Indicates                            | Example                    |
| ------------------ | ------------------------------- | ------------------------------------ | -------------------------- |
| `feature-*`        | Merge to dev                    | Feature code, unreviewed             | feature-user-auth          |
| `hotfix-*`         | Merge to dev/staging            | Emergency fix                        | hotfix-database-connection |
| `dev-version-*`    | Merge dev-version-update to dev | Version sync from prod               | dev-version-2.1.5          |
| `merged-feature-*` | Merge pre-release to staging    | Feature accepted & merged to staging | merged-feature-user-auth   |
| `alpha-version-*`  | Merge pre-release to staging    | Pre-production version (X.Y.Z)       | alpha-version-2.1.5        |
| `version-*`        | Merge staging to prod           | Production release (X.Y.Z)           | version-2.1.5              |

## Approval Workflows

### Pre-Release Creation Approval

**Who**: Product owner or release manager  
**Input**: Which feature tags to include  
**Decision**: MAJOR/MINOR/PATCH version bump  
**Output**: Pre-release branch created with PR

**Implementation**: Manual trigger button on Monitoring page, authenticated with GitHub OAuth

### Blue-Green Swap Approval

**Who**: Operations team or deployment approver  
**Input**: Confirmation that new version is tested  
**Decision**: Proceed with swap or rollback  
**Output**: Load balancer configuration updated

**Implementation**:

- Manual approval button on Monitoring page
- Approval workflow sends notification (email/Teams)
- Requires at least 2 approvers (or configurable)
- Logs all approvals for audit trail

## Error Handling & Rollback

### Cherry-Pick Conflicts

If cherry-picking feature commits results in conflicts:

1. Pause workflow, alert stakeholder
2. Manual intervention: resolve conflicts in pre-release branch
3. Resume workflow: continue PR creation

### Health Check Failures

If Prod (Green) health checks fail before swap:

1. Cancel swap, alert operations team
2. Log failure details
3. Option: rollback Prod (Green) to previous version or skip this swap
4. Keep Prod (Blue) active and safe

### Failed Merge

If PR merge to staging fails (conflicts, broken tests):

1. Reject merge
2. Create GitHub issue with details
3. Alert team to fix conflicts before retry

## Monitoring & Visibility

### Workflow Logging

All workflows must log:

- Workflow start/end timestamp
- Trigger event (which branch, which PR, which tag)
- All intermediate steps (cherry-picks, health checks, swaps)
- Success/failure status
- Any errors or warnings

### Tag Display on Monitoring Page

**Not Accepted Features** (on dev branch):

- Show all `feature-*` tags that do NOT have a corresponding `merged-feature-*` tag
- Display in order: newest first
- Include metadata: timestamp created, commit author, commit message snippet

**Accepted Features** (on staging/prod):

- Show all `merged-feature-*` tags (staging) or included in latest `version-*` (prod)
- Archive old merged features after 30 days

**Versions**:

- **Prod**: Latest `version-*` tag (only 1, the active version)
- **Staging**: Latest `alpha-version-*` tag
- **Dev**: All unaccepted `feature-*` tags

## Databricks Environment Updates

### Trigger-Based Updates

| Branch        | Environment  | Update Trigger                                         |
| ------------- | ------------ | ------------------------------------------------------ |
| dev           | DEV          | Auto on every merge to dev (new feature tag)           |
| dev (feature) | UA           | Manual (GitHub Actions button in Monitoring page)      |
| staging       | Staging      | Auto on every merge to staging (new alpha-version tag) |
| prod          | Prod (Green) | Auto on every merge to prod (before version tag)       |
| prod          | Prod (Blue)  | Manual swap approval                                   |

### Update Process

1. **Identify version to deploy**: From tag name (e.g., feature-auth → "feature-auth" checkout)
2. **Get latest code**: `git checkout [tag-or-branch]`
3. **Build artifacts**: Docker image, Python wheels, Databricks deployment config
4. **Deploy to environment**:
   - Stop old Databricks jobs/notebooks
   - Update code on Databricks
   - Verify schema compatibility
   - Start new jobs/notebooks
5. **Health checks**:
   - Databricks cluster healthy
   - Data pipeline runs without errors
   - Data freshness acceptable
6. **Log deployment**:
   - Version deployed
   - Timestamp
   - Success/failure
   - Any warnings

## Implementation Checklist

- [ ] Pre-release workflow cherry-picks correct commits
- [ ] Version increment logic handles MAJOR/MINOR/PATCH correctly
- [ ] Tag creation happens atomically with workflow
- [ ] Blue-Green health checks are comprehensive
- [ ] Swap approval requires manual confirmation
- [ ] All workflows log with timestamps and context
- [ ] Rollback procedures documented and tested
- [ ] Monitoring page reflects tag state accurately
- [ ] Error notifications sent to appropriate channels
- [ ] Audit trail captures all approvals and deployments

---

## Related Documentation

- **Git Branching Strategy**: See README.md "Git Branching Strategy and Deployment" section
- **Tag Display**: See plans/react-frontend.md for Monitoring page details
- **Environment Configuration**: See plans/ci-cd-specialist.md for Helm chart and infrastructure
