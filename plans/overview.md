# Repository Overview & Implementation Plan

**Last Updated**: 2026-07-26  
**Milestone Status**: 2 - Agent Readiness Review (Complete) → Moving to Milestone 3

---

## Overview

This repository (`cs-databricks`) is a **showcase project** for Azure Databricks and Power BI integration, demonstrating best practices for:

- **Data Collection**: Gathering statistics about countries using publicly available APIs
- **Data Transformation**: Using PySpark and Python to transform and clean data
- **Data Delivery**: Providing structured, validated data to Power BI for visualization
- **DevOps & Deployment**: Orchestrating Databricks environments across Azure with proper CI/CD, branching strategies, and monitoring

The project exemplifies modern cloud-native development practices including type safety, linting, testing, structured logging, and environment management with Blue-Green deployments.

---

## Repository Context

### Current State

**Existing Infrastructure:**

- ✅ Dev container setup (.devcontainer/) with Python, Node.js, Git, Azure CLI, and development tools
- ✅ GitHub Workflows for branching strategy (PR to dev/staging/prod, tag creation, environment updates)
- ✅ Azure Pipelines framework (.azuredevops/)
- ✅ Code linting/formatting config (ruff, yamllint, prettier, eslint)
- ✅ Pre-commit hooks configuration
- ✅ Python project structure (src/, tests/, notebooks/)
- ⚠️ Basic example code (example.py with simple math functions)
- ⚠️ Single notebook example (top_100_countries_population.ipynb)

**What's Working:**

- Basic project scaffolding and tooling
- Dev container allows reproducible local development
- GitHub Actions workflow files exist for the branching strategy

**What Needs Work:**

- Core data collection, transformation, and delivery logic
- Comprehensive test coverage (unit, integration, schema validation)
- Structured logging with proper context (currently basic)
- Data validation and schema enforcement
- Power BI integration layer
- Monitoring web page for environment/tag status
- Blue-Green deployment orchestration
- Documentation for each agent's responsibilities

### Git Branching Strategy (Already Designed)

The repository follows a sophisticated branching model with 3 permanent protected branches:

| Branch      | Purpose        | Accepts PRs From                        | Creates Tag                        | Environment       |
| ----------- | -------------- | --------------------------------------- | ---------------------------------- | ----------------- |
| **dev**     | Development    | feature-_, hotfix-_, dev-version-update | feature-_, hotfix-_, dev-version-* | DEV, UA           |
| **staging** | Pre-production | pre-release, hotfix-*                   | alpha-version-*                    | Staging           |
| **prod**    | Production     | staging                                 | version-*                          | Prod (Blue/Green) |

**Supporting Branches:**

- `feature-*`: Feature development, deleted after merge to dev
- `hotfix-*`: Emergency fixes, can merge to dev or staging
- `pre-release`: Auto-generated from accepted features, merges to staging
- `dev-version-update`: Auto-generated to sync prod version back to dev

**5 Environments:**

1. **DEV**: Latest dev branch code
2. **UA (User Acceptance)**: Feature tags for stakeholder review
3. **Staging**: Alpha versions for pre-production validation
4. **Prod (Blue)**: Active production environment
5. **Prod (Green)**: Inactive production environment for Blue-Green swap

---

## Requirements Summary

### Architecture & Code Structure

1. **Python Best Practices**
   - Type hints with `typy` enforcement
   - Linting with `ruff` (formatting and import rules)
   - Runtime validation with `pydantic`
   - Structured logging with timestamps and severity levels (Error, Warning, Info, Debug)

2. **Code Organization**
   - `src/`: All application logic
   - `src/notebooks/`: Jupyter notebooks (orchestration only, logic in .py files)
   - `tests/`: Unit tests with 100% mocking of external dependencies
   - Modular structure: nested functions moved to separate files
   - Type annotations on all public APIs

3. **Testing Strategy**
   - **Unit Tests**: Fast, isolated, mocked dependencies (test_* files in same structure as src/)
   - **Schema Tests**: Validate database schema, tables, columns
   - **Integration Tests**: Validate external API contracts and data pipelines
   - **Structural Tests**: Database server connectivity and structure validation

4. **Data Processing**
   - **Collection**: Public APIs (exact sources TBD with user)
   - **Transformation**: PySpark for distributed processing
   - **Validation**: Pydantic models, schema validation, data quality checks
   - **Delivery**: Structured data to Power BI

### DevOps & Deployment

1. **CI/CD Pipeline** (GitHub Actions + Azure Pipelines)
   - Automatic linting, type checking, testing on PRs
   - Tag creation on merge to protected branches
   - Automatic environment updates
   - Centralized, structured logging to Azure Log Analytics

2. **Environment Management**
   - Helm charts for Kubernetes deployment in Azure
   - Terraform for infrastructure (if needed)
   - Blue-Green deployment for Prod with manual swap approval
   - Resource cleanup for inactive Prod (Green)

3. **Monitoring & Observability**
   - Static web page showing:
     - Latest **version** tag on prod
     - Latest **alpha-version** tag on staging
     - All unaccepted **feature** tags on dev
     - Centralized logs (Error, Warning, Info only; Debug local-only)
   - Azure Log Analytics for centralized log aggregation

---

## Implementation Steps (High-Level)

### Phase 1: Foundation & Infrastructure (Agents: CI/CD Specialist, Python Agent, QA Agent)

1. **Logging Framework Setup**
   - Implement structured logger using `loguru` in `src/logging_config.py`
   - Timestamps, severity levels (DEBUG, INFO, WARNING, ERROR)
   - Configuration for Azure Log Analytics integration
   - Apply to all Python code and CI/CD workflows

2. **Pydantic Data Models**
   - Create `src/models/` folder for domain models
   - Define schemas for country data, API responses, and database records
   - Add validation logic and error handling

3. **API Client Framework**
   - Create `src/clients/` for external API integrations
   - Implement with proper error handling and logging
   - Design for testability (dependency injection)

4. **Database Layer**
   - Define Databricks/Spark schema in `src/database/schemas.py`
   - Connection utilities in `src/database/connection.py`
   - Query builders for common operations

5. **Test Infrastructure**
   - Set up pytest with mocking fixtures
   - Create mock data generators
   - Implement schema validation tests
   - Coverage reporting in CI/CD

### Phase 2: Data Processing Logic (Agents: Databricks Agent, Python Agent, Python Notebook Agent)

6. **Data Collection Module** (`src/data/collectors/`)
   - Implement collectors for each public API
   - Error handling and retry logic
   - Rate limiting and logging

7. **Data Transformation Module** (`src/data/transformers/`)
   - PySpark transformations for raw data
   - Data quality checks
   - Schema enforcement

8. **Data Delivery Module** (`src/data/delivery/`)
   - Write to Databricks (Power BI source)
   - Schema validation before write
   - Logging of record counts, errors, timing

9. **Notebook Orchestration**
   - Update `src/notebooks/` to call application modules
   - Minimal logic in notebooks (mostly parameter passing)
   - Execution logging and status reporting

### Phase 3: Validation & Quality (Agents: QA Agent, Python Agent)

10. **Unit Tests**
    - 100% coverage for business logic
    - Mock all external dependencies (APIs, DB, Spark)
    - Test error paths and edge cases

11. **Schema & Database Tests**
    - Validate database structure at startup
    - Test schema evolution
    - Connection pool tests

12. **Integration Tests**
    - End-to-end data pipeline test (mock APIs)
    - Staging area tests
    - Data quality verification

### Phase 4: Deployment & Monitoring (Agents: CI/CD Specialist, Azure Logic Apps Agent)

13. **Helm Chart Updates**
    - Configure for DEV, UA, Staging, Prod environments
    - Resource limits and scaling policies
    - Logging sidecars for centralized aggregation

14. **Azure Log Analytics Integration**
    - Set up Log Analytics workspace (if not exists)
    - Configure structured logging format
    - Create dashboards and alerts

15. **Monitoring Web Page**
    - React component showing:
      - Current prod version (latest **version-X.X.X** tag)
      - Current staging alpha version (latest **alpha-version-X.X.X** tag)
      - Dev branch feature tags (unaccepted **feature-*** tags)
    - Logs tab with filters by severity and date
    - Deployment: Static site in Azure Storage + CDN

16. **GitHub Actions Refinement**
    - Verify all workflow files work correctly
    - Add logging to workflow steps
    - Test tag creation on merges
    - Validate environment update triggers

### Phase 5: Blue-Green Deployment (Agents: CI/CD Specialist, Azure Logic Apps Agent)

17. **Blue-Green Orchestration**
    - Update prod (Green) when new version merged to prod branch
    - Manual approval UI for switching active environment
    - Automatic swap in Azure (load balancer/traffic manager)
    - Rollback capability if issues detected

18. **Pre-Release Automation**
    - Implement cherry-pick logic for pre-release branch creation
    - Auto-generate release notes from accepted features
    - Automatic PR creation to staging

### Phase 6: Power BI Integration (Agents: Power BI Agent, CI/CD Specialist)

19. **Power BI Data Connector**
    - Configure Databricks as Power BI data source
    - Create initial reports and dashboards
    - Document refresh schedule

20. **Data Quality Report**
    - Row counts, data freshness
    - Validation error rates
    - Performance metrics

---

## Validation Strategy

### Testing Gates Before Merge

- **Feature PR → dev**: Pass unit tests, linting, type checks, coverage > 80%
- **Pre-release PR → staging**: All tests pass, no schema conflicts
- **Staging PR → prod**: Manual review, staging environment stable for 24h
- **Prod swap**: Manual approval from stakeholders, health checks before switch

### Environment Smoke Tests

- DEV: Verify latest code deployed, notebooks run end-to-end
- UA: Feature tag available, users can test
- Staging: Alpha version deployed, all tests passing
- Prod (Blue): Active version serving traffic normally
- Prod (Green): Health checks pass before swap approval

### Monitoring Validation

- Logs flowing to Azure Log Analytics
- Monitoring page showing correct tags and logs
- Alert thresholds configured (error rates, latency, data freshness)

---

## Risks & Open Questions

### Risks

| Risk                                      | Severity | Mitigation                                                        |
| ----------------------------------------- | -------- | ----------------------------------------------------------------- |
| API rate limiting impacts data collection | Medium   | Implement backoff + queue for retries, monitor API quotas         |
| Schema evolution breaks pipelines         | Medium   | Version schemas, run migrations, validate before write            |
| Prod swap fails, old version needed       | Medium   | Keep Blue environment ready, test swap procedures, quick rollback |
| Logging volume causes cost spike          | Low      | Implement log sampling, set retention policies                    |
| Feature branch conflicts with dev         | Medium   | Require rebase before merge, use squash merge strategy            |

### Open Questions

1. **Which public APIs should be used for country data?**
   - Need specific API endpoints, documentation, rate limits, authentication
   - Affects data collection module design

2. **What are the exact Power BI report requirements?**
   - Key metrics, visualizations, refresh frequency
   - Affects data schema and delivery pipeline

3. **Azure infrastructure setup?**
   - Is Azure subscription, resource group, and Databricks instance ready?
   - Where should Helm charts be deployed (AKS cluster)?
   - Who is the Azure owner for permissions?

4. **Monitoring stakeholders?**
   - Who will approve Blue-Green swaps?
   - Who owns the Monitoring web page?
   - Escalation contacts for production issues?

5. **Data retention and privacy?**
   - How long should data be retained in Databricks?
   - Any PII or compliance requirements (GDPR, etc.)?

6. **Performance targets?**
   - SLA for data freshness? (hourly, daily refresh)
   - Max query latency for Power BI?
   - Peak data volume expectations?

---

## Handoff Notes

### For All Agents

- **Repository baseline**: Keep changes aligned with existing structure, use plans/overview.md as guideline
- **Agent plan files**: Create `plans/[agent-name].md` to track progress on your assigned tasks
- **Communication**: Update lead agent (Repository Planner) if tasks block each other or require other agents' changes
- **Quality bar**: Follow code review checklist, type safety with typy, linting with ruff, testing with pytest + mocks

### For CI/CD Specialist Agent

- **Responsibilities**: GitHub Actions workflows, Azure Pipelines, logging setup, monitoring page deployment, Blue-Green automation
- **Key files**: `.github/workflows/*.yml`, `.azuredevops/**`, Helm charts, Azure Log Analytics config
- **Dependencies**: Needs Azure subscription details, team consensus on logging format, approval workflow for Prod swaps
- **Deliverables**: Fully functional pipelines with centralized logging, working Monitoring web page, tested Blue-Green swap

### For Python/Databricks Agents

- **Responsibilities**: Core data collection, transformation, delivery logic; database layer; structured logging integration
- **Key files**: `src/data/`, `src/clients/`, `src/database/`, `src/models/`, `src/notebooks/`
- **Dependencies**: Exact API specs, Power BI schema requirements, Databricks connection details
- **Deliverables**: Production-ready modules with comprehensive tests, type hints, and documentation

### For QA Agent

- **Responsibilities**: Test strategy, unit tests, integration tests, schema validation, test fixtures and mocks
- **Key files**: `tests/`, test utilities, mock data generators
- **Dependencies**: Domain knowledge from Python agents, clarity on data sources and business rules
- **Deliverables**: Test suite with > 80% coverage, schema validation tests, data quality checks

### For React/Monitoring Agent

- **Responsibilities**: Monitoring web page UI, log viewer, tag display, Azure integration
- **Key files**: `src/monitoring/` (new), static site deployment
- **Dependencies**: Azure Log Analytics access, team consensus on UI design, GitOps details for web page deployment
- **Deliverables**: Working Monitoring page with logs and tag visualization, deployment pipeline

### For Azure Logic Apps Agent

- **Responsibilities**: Complex orchestration workflows (Blue-Green swap, pre-release creation, environment triggers)
- **Key files**: `.azuredevops/` orchestration, Azure Logic Apps definitions
- **Dependencies**: Approval workflow design, Azure infrastructure details, GitHub API access
- **Deliverables**: Functional orchestrations for pre-release creation and Blue-Green swap

### For Power BI Agent

- **Responsibilities**: Power BI reports and dashboards, data source configuration
- **Key files**: Power BI `.pbix` files (stored separately), data refresh configuration
- **Dependencies**: Databricks schema, business requirements for reports, refresh frequency
- **Deliverables**: Initial Power BI reports demonstrating data quality and insights

---

## Milestone 2 Completion: Agent Readiness ✅

**Status**: Complete  
**Date Completed**: 2026-07-26

### What Was Delivered

#### 1. Five New Custom Instructions Created

All agents now have project-specific instructions that explain Databricks concepts and expected patterns:

- **`databricks-python-best-practices.instructions.md`**
  - Type hints with typy enforcement
  - Pydantic data validation patterns
  - Structured logging with loguru
  - Testing patterns with mocks
  - PySpark best practices
  - API client patterns (REST Countries, World Bank)

- **`databricks-orchestration.instructions.md`**
  - Pre-release branch creation workflow (manually triggered)
  - Staging merge automation (tag creation)
  - Production merge automation (version tags)
  - Blue-Green swap approval workflow
  - Dev-version-update sync process
  - Design decisions (only unaccepted feature tags display, manual cherry-pick)
  - Data sources: REST Countries API & World Bank API

- **`database-schema-validation-testing.instructions.md`**
  - Schema definition patterns
  - Schema validation tests
  - Data quality tests (row counts, nulls, uniqueness, freshness)
  - Mock database fixtures
  - Database validator utility class
  - Pydantic model testing patterns

- **`monitoring-web-page-ui.instructions.md`**
  - React component structure (App, VersionsPage, FeaturesPage, LogsPage)
  - Deployment status cards
  - Feature tag display (unaccepted only)
  - Centralized logs viewer with filtering
  - Manual action buttons (UA update, Blue-Green swap)
  - Azure Log Analytics integration
  - GitHub Tags API integration
  - Static deployment to Azure Storage + CDN

- **`power-bi-databricks-integration.instructions.md`**
  - Databricks connector setup (PAT and Azure AD auth)
  - SQL endpoint configuration
  - Data model design (star schema)
  - Staging table patterns for Power BI
  - DAX measures and KPIs
  - Dashboard design (Country Statistics, Pipeline Health, Executive Summary)
  - Query folding and performance optimization
  - Scheduled refresh configuration
  - Security & monitoring

#### 2. All Agent Files Enhanced

Updated 7 agent files with:

- **Task-specific descriptions** that clarify each agent's role in the project
- **New custom instructions** pointing to project guidelines
- **Relevant skills** from Copilot's available skills library
- **Azure tools** for infrastructure and API access

| Agent                  | Role Enhancement                                     | Instructions Added                               | Skills Added                                                               |
| ---------------------- | ---------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| CI/CD Specialist       | Databricks orchestration, Blue-Green, tag management | 5 (including databricks-orchestration)           | None (uses built-in K8s, Terraform, GitHub Actions)                        |
| Databricks Agent       | PySpark pipelines, data collection/transform         | 4 (including databricks-python-best-practices)   | python-fact-grounded-coding, pylance-refactoring, pylance-python-profiling |
| Python Notebook Agent  | Databricks orchestration notebooks                   | 3 (including databricks-python-best-practices)   | python-fact-grounded-coding, pylance-python-profiling                      |
| QA Agent               | Schema & data quality testing                        | 3 (including database-schema-validation-testing) | python-fact-grounded-coding                                                |
| React Frontend Agent   | Monitoring web page                                  | 3 (including monitoring-web-page-ui)             | None (uses built-in React tools)                                           |
| Azure Logic Apps Agent | Pre-release & Blue-Green workflows                   | 3 (including databricks-orchestration)           | None (uses built-in Azure Logic Apps tools)                                |
| Power BI Agent         | Databricks reporting                                 | 2 (including power-bi-databricks-integration)    | None (uses built-in Power BI tools)                                        |

#### 3. Design Decisions Documented

All ambiguities from Milestone 1 have been resolved in the instructions:

- **Tag Display**: Only **unaccepted** feature tags show on Monitoring page (feature-* without merged-feature-*)
- **Pre-release Creation**: Manual trigger (not automatic) via UI button or API call
- **Data Sources**:
  - REST Countries API: https://restcountries.com/
  - World Bank API: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information
- **Blue-Green Swap**: Requires manual approval with health checks before switch
- **Logging**: All environments send Info/Warning/Error to Azure Log Analytics; Debug only local

---

## Next Steps: Milestone 3 (Agent Handoff & Implementation)

### Ready for Milestone 3?

**YES** ✅ All agents are equipped with:

1. Clear role definitions in agent.md files
2. Project-specific instructions for their domain
3. Relevant Copilot skills assigned
4. Understanding of Databricks, Python, and CI/CD patterns

### Milestone 3 Workflow

For each agent:

1. **Create agent-specific plan**: Each agent creates `plans/[agent-name].md` with:
   - Their assigned responsibilities (from overview.md handoff notes)
   - Refined implementation steps for their tasks
   - Dependencies on other agents
   - Success criteria for their deliverables

2. **Refinement phase**:
   - Agent reviews their plan
   - Identifies blockers or ambiguities
   - Communicates back to Repository Planner if changes needed

3. **Implementation begins**:
   - Agent starts coding following their plan
   - Updates `plans/[agent-name].md` with progress
   - Reports blockers or handoff to other agents

### Agent Scheduling (Suggested)

**Phase 1 (Parallel): Foundation**

- Python/Databricks agents: Implement models, clients, database layer
- QA agent: Design test framework and fixtures
- CI/CD specialist: Set up GitHub Actions and Helm charts

**Phase 2 (Parallel): Core Logic**

- Databricks agents: Build collectors, transformers, delivery
- Python Notebook agent: Create orchestration notebooks

**Phase 3 (Parallel): Quality & Visibility**

- QA agent: Write comprehensive tests
- React Frontend agent: Build Monitoring page
- Power BI agent: Create dashboards

**Phase 4 (Sequential): Orchestration & Deployment**

- Azure Logic Apps agent: Implement pre-release and Blue-Green workflows
- CI/CD specialist: Integrate all workflows and test end-to-end

---

## Appendix: File Structure Reference

```
/workspaces/cs-databricks/
├── .github/
│   ├── agents/
│   │   ├── ci-cd-specialist.agent.md        # ✅ Updated with instructions & tools
│   │   ├── databricks-agent.agent.md         # ✅ Updated with instructions & skills
│   │   ├── python-notebook.agent.md          # ✅ Updated with instructions & skills
│   │   ├── react-frontend.agent.md           # ✅ Updated with instructions & tools
│   │   ├── qa.agent.md                       # ✅ Updated with instructions & skills
│   │   ├── azure-logic-apps.agent.md         # ✅ Updated with instructions & tools
│   │   ├── power-bi.agent.md                 # ✅ Updated with instructions & tools
│   │   └── planner.agent.md                  # Repository Planner (this agent)
│   ├── instructions/
│   │   ├── databricks-python-best-practices.instructions.md          # ✅ NEW
│   │   ├── databricks-orchestration.instructions.md                  # ✅ NEW
│   │   ├── database-schema-validation-testing.instructions.md        # ✅ NEW
│   │   ├── monitoring-web-page-ui.instructions.md                   # ✅ NEW
│   │   ├── power-bi-databricks-integration.instructions.md           # ✅ NEW
│   │   └── [other existing instructions...]
│   └── workflows/                            # GitHub Actions (existing)
├── .azuredevops/                             # Azure Pipelines (existing)
├── .devcontainer/                            # Dev container (existing)
├── .databricks/                              # Databricks config (existing)
├── src/
│   ├── __init__.py
│   ├── example.py                            # (To be replaced)
│   ├── logging_config.py                     # (To be created - Phase 1)
│   ├── models/                               # (To be created - Phase 1)
│   ├── clients/                              # (To be created - Phase 1)
│   │   ├── base.py                           # Base HTTP client
│   │   ├── rest_countries.py                 # REST Countries API client
│   │   └── world_bank.py                     # World Bank API client
│   ├── database/                             # (To be created - Phase 1)
│   │   ├── schemas.py                        # Databricks schema definitions
│   │   ├── connection.py                     # Spark session management
│   │   └── validators.py                     # Schema validation utilities
│   ├── data/
│   │   ├── collectors/                       # (To be created - Phase 2)
│   │   │   ├── rest_countries.py
│   │   │   └── world_bank.py
│   │   ├── transformers/                     # (To be created - Phase 2)
│   │   │   └── country_transform.py
│   │   └── delivery/                         # (To be created - Phase 2)
│   │       └── spark_writer.py
│   ├── notebooks/
│   │   ├── country_stats_pipeline.ipynb      # (To be updated - Phase 2)
│   │   └── outputs/                          # (existing)
│   └── monitoring/                           # (To be created - Phase 3)
│       ├── src/
│       │   ├── App.tsx
│       │   ├── pages/
│       │   ├── components/
│       │   ├── api/
│       │   └── hooks/
│       └── public/
├── tests/
│   ├── unit/                                 # (To be created - Phase 1+3)
│   │   ├── test_models.py
│   │   ├── test_collectors.py
│   │   ├── test_transformers.py
│   │   └── test_delivery.py
│   ├── integration/                          # (To be created - Phase 3)
│   │   ├── test_spark_schema.py
│   │   ├── test_database_structure.py
│   │   └── test_pipeline_end_to_end.py
│   └── fixtures/                             # (To be created - Phase 1)
│       ├── conftest.py
│       ├── mock_data.py
│       └── mock_spark.py
├── plans/
│   ├── overview.md                           # ✅ This file (Milestone 2 complete)
│   ├── ci-cd-specialist.md                   # (To be created - Milestone 3)
│   ├── databricks-agent.md                   # (To be created - Milestone 3)
│   ├── python-notebook-agent.md              # (To be created - Milestone 3)
│   ├── qa-agent.md                           # (To be created - Milestone 3)
│   ├── react-frontend-agent.md               # (To be created - Milestone 3)
│   ├── azure-logic-apps-agent.md             # (To be created - Milestone 3)
│   └── power-bi-agent.md                     # (To be created - Milestone 3)
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

**Document Status**: Milestone 2 Complete  
**Ready for**: Milestone 3 Agent Handoff
