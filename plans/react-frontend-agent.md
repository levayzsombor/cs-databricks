# React Frontend Agent - Implementation Plan

**Agent**: React Frontend Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 3 (Quality & Visibility)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Build the Monitoring web page React application that displays Databricks environment status, feature tags, and centralized logs from Azure Log Analytics. Display version information, action buttons for UA updates and Blue-Green swaps, and real-time log viewer with filtering.

**Key Instructions to Follow**:

- monitoring-web-page-ui.instructions.md
- code-review-generic.instructions.md
- context-engineering.instructions.md

---

## Phase 3: Quality & Visibility (Week 3-4)

### Task 3.1: Project Setup & Base Components

**Objective**: Initialize React project with TypeScript, routing, and styling

**Steps**:

1. Create React project in `src/monitoring/`:
   - Use Vite for fast development
   - Configure TypeScript with strict mode
   - Set up ESLint and Prettier
   - Configure Tailwind CSS or Material-UI for styling
2. Create directory structure:
   - `src/components/` - Reusable components
   - `src/pages/` - Page components (Versions, Features, Logs)
   - `src/api/` - API integration (GitHub, Azure Log Analytics)
   - `src/hooks/` - Custom React hooks
   - `src/types/` - TypeScript interfaces
3. Create base App.tsx:
   - Tab navigation (Versions, Features, Logs)
   - Auto-refresh hook (30-second polling)
   - Error boundary for graceful error handling
   - Loading states
4. Create utility functions:
   - Format dates and timestamps
   - Parse GitHub tag names
   - Filter logs by severity/date
   - Calculate environment status

**Deliverables**:

- ✅ React project initialized with TypeScript
- ✅ Directory structure created
- ✅ Base App.tsx with tab navigation
- ✅ Utility functions for common operations

**Dependencies**:

- Node.js environment (in devcontainer)
- GitHub API access for tags
- Azure Log Analytics access

**Success Criteria**:

- React app starts successfully (`npm run dev`)
- TypeScript compiles without errors
- Basic navigation works
- No console warnings

---

### Task 3.2: Versions Page Component

**Objective**: Display current environment versions

**Steps**:

1. Create `src/pages/VersionsPage.tsx`:
   - Display 3 status cards:
     - **Prod Active**: Latest version-* tag deployed to Prod (Blue)
       - Show tag name, deployment date, commit hash
     - **Staging Alpha**: Latest alpha-version-* tag deployed to Staging
       - Show tag name, deployment date, commit hash
     - **Dev Branch**: Show latest dev branch commit
       - Show commit hash, author, date
2. Create `src/components/DeploymentStatus.tsx`:
   - Card component showing environment status
   - Health indicator (green = healthy, red = error, yellow = warning)
   - Timestamp of last update
   - Link to deployment logs
3. Create API integration:
   - `src/api/github.ts`: Fetch tags from GitHub API
     - Get all tags with metadata
     - Filter by pattern (version-_, alpha-version-_, feature-*)
     - Sort by date (newest first)
   - Handle GitHub API rate limiting and errors
4. Data refresh:
   - Auto-refresh every 30 seconds
   - Show "last updated" timestamp
   - Handle network errors gracefully

**Deliverables**:

- ✅ `src/pages/VersionsPage.tsx` - versions display
- ✅ `src/components/DeploymentStatus.tsx` - status card component
- ✅ GitHub API integration for tags
- ✅ Auto-refresh functionality

**Dependencies**:

- GitHub API access with personal access token
- Base App component from Task 3.1

**Success Criteria**:

- Versions page displays all 3 environment versions
- Status cards show correct information
- Auto-refresh works every 30 seconds
- API errors handled gracefully

---

### Task 3.3: Features Page Component

**Objective**: Display unaccepted feature tags

**Steps**:

1. Create `src/pages/FeaturesPage.tsx`:
   - Display **only unaccepted feature tags**
     - feature-* tags WITHOUT corresponding merged-feature-* tag
   - Each feature card shows:
     - Feature name
     - Author and creation date
     - Commit message
     - Link to PR
     - Status: "Awaiting Acceptance"
   - Sort options (newest first, oldest first, alphabetical)
   - Filter by author or search by name
2. Create `src/components/FeatureCard.tsx`:
   - Card component for each feature
   - Visual indicator (blue = pending)
   - Actions (view PR, view commits)
3. Implement feature acceptance tracking:
   - Query GitHub API for feature-* tags
   - Query for merged-feature-* tags
   - Diff to find unaccepted features
   - Cache results for 1 minute
4. Data refresh:
   - Auto-refresh every 30 seconds
   - Show "Features Awaiting Acceptance" count

**Deliverables**:

- ✅ `src/pages/FeaturesPage.tsx` - features display
- ✅ `src/components/FeatureCard.tsx` - feature card component
- ✅ Logic to identify unaccepted features
- ✅ Sorting and filtering functionality

**Dependencies**:

- GitHub API integration from Task 3.2

**Success Criteria**:

- Only unaccepted features are displayed
- Feature cards show all required information
- Sorting and filtering work correctly
- Auto-refresh works

---

### Task 3.4: Logs Page Component

**Objective**: Display centralized logs from Azure Log Analytics

**Steps**:

1. Create `src/pages/LogsPage.tsx`:
   - Table of logs from last 24 hours
   - Columns: Timestamp, Severity, Environment, Message
   - Each row is expandable to show full context
2. Create log filters:
   - Severity filter (Error, Warning, Info, all)
   - Environment filter (DEV, UA, Staging, Prod)
   - Date range picker (last 1h, 6h, 24h)
   - Text search (search message content)
   - Auto-filter to last 24 hours by default
3. Create `src/api/loganalytics.ts`:
   - Query Azure Log Analytics using KQL
   - Parse timestamp, severity, environment, message
   - Handle pagination (show 100 logs per page)
   - Cache results for 30 seconds
4. Create `src/components/LogsTable.tsx`:
   - Paginated table of logs
   - Color-coded severity (red = error, yellow = warning, blue = info)
   - Expandable rows for full log context
   - "Copy" button to copy log to clipboard
5. Error handling:
   - Show friendly message if query fails
   - Retry on network errors
   - Show "loading" indicator while fetching

**Deliverables**:

- ✅ `src/pages/LogsPage.tsx` - logs display
- ✅ `src/api/loganalytics.ts` - Log Analytics query integration
- ✅ `src/components/LogsTable.tsx` - logs table component
- ✅ Filter and search functionality

**Dependencies**:

- Azure Log Analytics credentials (service principal or MSI)
- KQL query knowledge
- Log Analytics workspace configured by CI/CD Agent

**Success Criteria**:

- Logs load from Azure Log Analytics
- Filters work correctly
- Search finds relevant logs
- Table is responsive and readable

---

### Task 3.5: Action Buttons & Manual Controls

**Objective**: Implement action buttons for UA updates and Blue-Green swaps

**Steps**:

1. Create `src/components/ActionButtons.tsx`:
   - Button 1: "Update UA to Dev"
     - Fetches latest dev branch commit
     - Triggers deployment to UA environment
     - Shows loading indicator
     - Shows success/error message
   - Button 2: "Approve Blue-Green Swap"
     - Shows current Prod (Blue) and Green versions
     - Requires 2+ approvers (for multi-user setup)
     - Shows approval status
     - Confirms swap before execution
2. Create approval workflow:
   - Display current approvers
   - Add approval checkbox if user authenticated
   - Show approval count (2/2 needed, etc.)
   - Disable swap button until threshold met
3. Create API integration:
   - `src/api/deployments.ts`: Trigger deployments
     - POST to deployment API endpoint
     - Pass environment, version, approver info
     - Handle async deployment tracking
4. Create notification system:
   - Toast notifications for actions
   - Temporary success/error messages
   - Link to deployment logs

**Deliverables**:

- ✅ `src/components/ActionButtons.tsx` - action buttons
- ✅ `src/api/deployments.ts` - deployment API integration
- ✅ Approval workflow implementation
- ✅ Notification system

**Dependencies**:

- CI/CD Specialist (deployment API endpoint)
- Azure Logic Apps Agent (orchestration workflow)
- Authentication/authorization system

**Success Criteria**:

- Buttons are visible and clickable
- "Update UA to Dev" triggers deployment
- "Approve Blue-Green Swap" requires approvals
- Notifications show action status

---

### Task 3.6: Styling & Responsiveness

**Objective**: Apply consistent styling and ensure mobile responsiveness

**Steps**:

1. Apply design system:
   - Use Tailwind CSS classes or Material-UI components
   - Consistent color scheme (blues for info, reds for errors, greens for success)
   - Standard padding, margins, border radius
   - Font sizes and weights
2. Create responsive layout:
   - Mobile-first design (works on phones/tablets)
   - Breakpoints for tablet and desktop
   - Collapsible navigation on mobile
   - Tables scroll horizontally on small screens
3. Create dark mode support (optional):
   - Toggle dark/light theme
   - Store preference in localStorage
   - Use Tailwind's dark mode or Material-UI theme
4. Accessibility:
   - ARIA labels on buttons
   - Semantic HTML (`<button>`, `<table>`, etc.)
   - Keyboard navigation (Tab, Enter, Escape)
   - Color contrast ratios meet WCAG AA

**Deliverables**:

- ✅ Consistent styling across all pages
- ✅ Responsive design on all screen sizes
- ✅ Accessibility features implemented
- ✅ Dark mode support (optional)

**Dependencies**:

- All page and component files from Tasks 3.2-3.5

**Success Criteria**:

- App looks good on desktop, tablet, mobile
- All buttons/links are keyboard accessible
- Color contrast meets WCAG AA
- No console warnings

---

### Task 3.7: Deployment & Static Site

**Objective**: Build and deploy monitoring web page as static site

**Steps**:

1. Create build configuration:
   - `npm run build` generates optimized dist/ folder
   - Configure base path for deployment (if needed)
   - Minify JavaScript and CSS
   - Generate source maps for debugging
2. Deploy to Azure Static Web Apps:
   - Push built files to Azure Static Web Apps
   - Configure custom domain (if available)
   - Enable HTTPS
   - Set cache headers (cache pages 24h, refresh data 5m)
3. Create GitHub Actions workflow:
   - On push to main/dev: build and deploy
   - Run ESLint and build checks before deploy
   - Report build status
4. Create deployment documentation:
   - How to deploy locally
   - How to deploy to Azure
   - Environment variables needed
   - Troubleshooting guide

**Deliverables**:

- ✅ Build configuration working
- ✅ Deployment to Azure Static Web Apps
- ✅ GitHub Actions deployment workflow
- ✅ Deployment documentation

**Dependencies**:

- Azure Static Web Apps resource created
- CI/CD Agent (GitHub Actions integration)

**Success Criteria**:

- Build completes without errors
- App deploys to Azure successfully
- App is accessible via URL
- Page loads in < 2 seconds

---

## Cross-Agent Dependencies

**Blocks**:

- Blocks: No other agents (frontend runs independently)

**Depends On**:

- CI/CD Agent (GitHub API, Azure Log Analytics, deployment endpoints)
- Azure Logic Apps Agent (approval workflow API)

---

## Success Criteria for Milestone 3

✅ React project initialized with TypeScript  
✅ Versions page shows Prod/Staging/Dev versions  
✅ Features page displays unaccepted features  
✅ Logs page shows Azure Log Analytics data  
✅ Action buttons for UA update and Blue-Green swap  
✅ Responsive design on all screen sizes  
✅ Accessibility features implemented  
✅ Deployed to Azure Static Web Apps

---

## Risks & Mitigations

| Risk                                   | Mitigation                                            |
| -------------------------------------- | ----------------------------------------------------- |
| API rate limits from GitHub/Azure      | Implement caching; cache results for 30-60 seconds    |
| Azure Log Analytics queries too slow   | Optimize KQL queries; add indexes if possible         |
| Mobile layout breaks on small screens  | Test on real devices; use responsive design framework |
| Authentication/authorization not ready | Build without auth initially; add later if needed     |

---

## Handoff Checklist

- [ ] React project initialized with TypeScript
- [ ] Versions page displays environment versions
- [ ] Features page shows unaccepted feature tags
- [ ] Logs page queries Azure Log Analytics
- [ ] Action buttons for deployments
- [ ] Responsive design tested on mobile/tablet/desktop
- [ ] Accessibility features implemented
- [ ] Styling applied consistently
- [ ] Deployed to Azure Static Web Apps
- [ ] GitHub Actions deployment workflow working

**When Complete**: Report back to Repository Planner with completion status and any blockers.
