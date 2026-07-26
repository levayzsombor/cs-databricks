# Azure Logic Apps Agent - Implementation Plan

**Agent**: Azure Logic Apps Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 4 (Sequential Orchestration & Deployment)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Design and implement Azure Logic Apps workflows for pre-release cherry-picking, Blue-Green deployment approval, and tag-based environment updates. Workflows orchestrate GitHub API, Databricks, and manual approval steps using Workflow Definition Language (WDL).

**Key Instructions to Follow**:

- azure-logic-apps-power-automate.instructions.md
- databricks-orchestration.instructions.md
- azure-naming.instructions.md

---

## Phase 4: Orchestration & Deployment (Week 3-4)

### Task 4.1: Pre-Release Cherry-Pick Workflow

**Objective**: Implement manual pre-release branch creation with feature selection

**Steps**:

1. Create `pre-release-cherry-pick.logicapp.json`:
   - Trigger: Manual (from React Monitoring page)
   - Input parameters:
     - Selected feature commits (array of commit SHAs)
     - Target base (default: "dev")
     - Release notes title and description

2. Workflow steps:
   - **Step 1**: Validate inputs
     - Check commits are valid
     - Check all commits are from feature branches
     - Log validation result

   - **Step 2**: Create pre-release branch
     - Branch name: "pre-release-YYYY-MM-DD-HHmmss"
     - Based on dev branch
     - API call: `POST /repos/{owner}/{repo}/git/refs`

   - **Step 3**: Cherry-pick selected commits
     - Loop through each commit SHA
     - API call: Git cherry-pick (via Databricks or GitHub API)
     - Handle conflicts: Log and notify user
     - Update branch with cherry-picked commits

   - **Step 4**: Generate release notes
     - Parse commit messages for release notes
     - Format as markdown
     - Add deployment date and author

   - **Step 5**: Create pull request to staging
     - Title: "Release: YYYY-MM-DD pre-release"
     - Body: Generated release notes
     - Labels: "pre-release", "auto-generated"
     - API call: `POST /repos/{owner}/{repo}/pulls`

   - **Step 6**: Notify on success/failure
     - Send notification to Slack or Teams
     - Include PR link
     - Include release notes preview

   - **Step 7**: Log workflow execution
     - Timestamp, author, selected features
     - Pre-release branch name
     - PR link

3. Error handling:
   - Cherry-pick conflicts: Pause and notify user
   - API failures: Retry up to 3 times
   - Invalid commits: Reject and notify user
   - All errors logged to Azure Log Analytics

**Deliverables**:

- ✅ `pre-release-cherry-pick.logicapp.json` - pre-release workflow
- ✅ GitHub API integration for branch/PR creation
- ✅ Error handling and conflict resolution
- ✅ Slack/Teams notifications

**Dependencies**:

- GitHub API access with personal access token
- Azure Logic Apps resource created
- GitHub repository connection configured

**Success Criteria**:

- Pre-release branch created successfully
- Commits cherry-picked correctly
- PR created with release notes
- Notifications sent on completion

---

### Task 4.2: Blue-Green Deployment Approval Workflow

**Objective**: Implement approval workflow for production Blue-Green swaps

**Steps**:

1. Create `blue-green-swap-approval.logicapp.json`:
   - Trigger: Manual (from React Monitoring page)
   - Input parameters:
     - Current Prod (Blue) version
     - New Prod (Green) version
     - Approvers list (array of emails)

2. Workflow steps:
   - **Step 1**: Prepare environment details
     - Fetch Blue environment status
     - Fetch Green environment status
     - Compare versions and deployment dates

   - **Step 2**: Run health checks on Green
     - Call Databricks API to check Green cluster status
     - Verify notebooks can be executed
     - Verify tables are accessible
     - Log health check results

   - **Step 3**: Create approval request
     - Send approval email to each approver
     - Include Blue/Green version comparison
     - Include health check results
     - Include rollback instructions
     - Approval link with approve/reject options

   - **Step 4**: Wait for approvals (parallel)
     - Wait for responses from all approvers
     - Timeout after 1 hour
     - Track approval status

   - **Step 5**: Validate approval threshold
     - Check if 2+ approvals received
     - Check if any rejections
     - If rejected: Notify and abort
     - If approved: Proceed to swap

   - **Step 6**: Perform Blue-Green swap
     - Update load balancer/traffic manager
     - Route traffic from Blue to Green
     - Verify traffic routing works
     - Log swap execution

   - **Step 7**: Post-swap validation
     - Monitor Green (now active) for errors
     - Check application logs for errors
     - If errors detected: Rollback to Blue
     - If successful: Mark swap as complete

   - **Step 8**: Notify approvers of outcome
     - Success email with new active version
     - Or failure email with rollback details
     - Include metrics (response time, error rate)

3. Error handling:
   - Health checks fail: Abort swap, notify approvers
   - Approval timeout: Abort swap
   - Traffic routing fails: Automatic rollback
   - Post-swap errors: Automatic rollback to Blue
   - All errors logged to Azure Log Analytics

**Deliverables**:

- ✅ `blue-green-swap-approval.logicapp.json` - approval workflow
- ✅ Health check integration
- ✅ Approval request and tracking
- ✅ Automated rollback on failure
- ✅ Email/Slack notifications

**Dependencies**:

- Azure Logic Apps resource created
- Databricks API access
- Load balancer/traffic manager access
- Email/Slack connectors configured

**Success Criteria**:

- Approval emails sent successfully
- Approvals tracked correctly
- Blue-Green swap executes successfully
- Rollback works if swap fails
- All steps logged and auditable

---

### Task 4.3: Environment Update Trigger Workflows

**Objective**: Implement automatic environment updates on tag creation

**Steps**:

1. Create `dev-environment-update.logicapp.json`:
   - Trigger: GitHub tag created matching "dev-*"
   - Steps:
     - Fetch new version/tag details
     - Trigger Helm deployment to DEV environment
     - Wait for deployment to complete (30 min timeout)
     - Verify deployment health
     - Log completion
   - Error handling: Alert if deployment fails

2. Create `staging-environment-update.logicapp.json`:
   - Trigger: GitHub tag created matching "alpha-version-*"
   - Steps:
     - Fetch alpha version details
     - Trigger Helm deployment to Staging environment
     - Wait for deployment to complete
     - Verify deployment health
     - Log completion
   - Error handling: Alert if deployment fails

3. Create `prod-environment-update.logicapp.json`:
   - Trigger: GitHub tag created matching "version-*"
   - Steps:
     - Fetch production version details
     - Trigger Helm deployment to Prod (Green) environment
     - Wait for deployment to complete
     - Verify Green environment health
     - Wait for manual approval for swap (via blue-green-swap-approval workflow)

**Deliverables**:

- ✅ `dev-environment-update.logicapp.json` - DEV auto-update
- ✅ `staging-environment-update.logicapp.json` - Staging auto-update
- ✅ `prod-environment-update.logicapp.json` - Prod deployment to Green

**Dependencies**:

- GitHub webhook configured for tag creation events
- Azure Logic Apps HTTP triggers configured
- Helm deployment API/scripts ready

**Success Criteria**:

- Environment updates triggered automatically on tag creation
- Deployments complete successfully
- Health checks verify deployment
- Failures are alerted

---

### Task 4.4: Workflow Management & Monitoring

**Objective**: Implement monitoring and management of Logic Apps workflows

**Steps**:

1. Create workflow documentation:
   - Document each workflow's purpose
   - Document trigger conditions
   - Document input/output parameters
   - Document error scenarios and resolutions

2. Set up monitoring:
   - Configure Azure Monitor alerts
   - Alert on workflow failures
   - Alert on long execution times (> 30 min)
   - Dashboard showing workflow stats

3. Create run history view:
   - Query Logic Apps run history
   - Show recent runs (success/failure)
   - Show execution times
   - Show error messages

4. Create manual controls:
   - Ability to disable workflows temporarily
   - Ability to rerun failed workflows
   - Ability to cancel running workflows

5. Integration with React Monitoring page:
   - Show workflow status in Monitoring page
   - Show recent workflow runs
   - Link to detailed run information

**Deliverables**:

- ✅ Workflow documentation
- ✅ Azure Monitor alerts configured
- ✅ Monitoring dashboard
- ✅ Integration with React page

**Dependencies**:

- All Logic Apps workflows created
- Azure Monitor resource configured

**Success Criteria**:

- Workflows can be monitored
- Failures are alerted
- Documentation is complete
- React page shows workflow status

---

## Cross-Agent Dependencies

**Blocks**:

- Blocks: CI/CD Specialist (orchestration for environment updates)

**Depends On**:

- GitHub API access and webhook configuration
- Databricks API access
- Load balancer/traffic manager configuration
- React Frontend Agent (approval UI)

---

## Success Criteria for Milestone 3

✅ Pre-release cherry-pick workflow functional  
✅ Blue-Green swap approval workflow working  
✅ Environment update triggers on tag creation  
✅ All workflows monitored and alerted  
✅ Approval workflow requires 2+ approvals  
✅ Automatic rollback on swap failure  
✅ All steps logged to Azure Log Analytics

---

## Risks & Mitigations

| Risk                                  | Mitigation                                          |
| ------------------------------------- | --------------------------------------------------- |
| Approval email goes to spam           | Test email delivery; use Teams integration instead  |
| Cherry-pick conflicts hard to resolve | Provide UI to resolve conflicts; allow manual merge |
| Blue-Green swap causes data loss      | Test rollback procedure; validate data integrity    |
| Workflow executes too long            | Optimize steps; set shorter timeouts where possible |
| GitHub API rate limits                | Cache API responses; use GitHub App instead of PAT  |

---

## Handoff Checklist

- [ ] Pre-release cherry-pick workflow functional
- [ ] Blue-Green swap approval workflow with health checks
- [ ] Environment update triggers working
- [ ] Approval workflow requires 2+ approvals
- [ ] Automatic rollback implemented
- [ ] Notifications sent on success/failure
- [ ] All workflows monitored
- [ ] Documentation complete
- [ ] Error handling tested
- [ ] Integration with React Monitoring page

**When Complete**: Report back to Repository Planner with completion status and any blockers.
