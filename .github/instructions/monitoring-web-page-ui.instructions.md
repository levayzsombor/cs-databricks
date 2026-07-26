---
description: 'UI and implementation patterns for the Monitoring web page, displaying branch versions, feature tags, and centralized logs from Azure Log Analytics'
applyTo: 'src/monitoring/**'
---

# Monitoring Web Page UI Patterns

Guidelines for building the Monitoring web page that displays Databricks environment status, deployment versions, and centralized application logs.

## Overview

The Monitoring page is a **static React web application** deployed to Azure Storage + CDN. It serves as the central hub for observing:

1. **Version Status**: Current versions deployed to prod, staging, and dev
2. **Feature Acceptance**: Unaccepted feature tags awaiting stakeholder review
3. **Centralized Logs**: Application logs from all environments (Info, Warning, Error)
4. **Manual Triggers**: UI buttons for UA environment update and Blue-Green swap approval

## Design Principles

- **Read-Only by Default**: Display system state, not editable data (except for approval buttons)
- **Real-Time Updates**: Fetch latest tags and logs every 30 seconds
- **Clear Status**: Visual indicators for environment health and version maturity
- **Minimal Latency**: Cached log queries, efficient Azure API calls
- **Responsive Design**: Works on desktop, tablet, and mobile

## Technology Stack

- **Frontend**: React 18+ with TypeScript
- **State Management**: React hooks (useState, useEffect, useContext)
- **HTTP Client**: Axios or Fetch API
- **UI Framework**: Material-UI or Tailwind CSS
- **Charts**: Recharts for log visualization (optional)
- **Build**: Vite or Create React App
- **Deployment**: Azure Static Web Apps or Azure Storage + CDN

## Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Monitoring Dashboard                        [Refresh] [Help] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  DEPLOYMENT STATUS                                            │
│  ┌────────────────┬──────────────────┬────────────────┐      │
│  │ Prod (Active)  │ Staging (Alpha)  │ Dev (Features) │      │
│  │ version-2.1.5  │ alpha-v-2.1.0    │ 3 unaccepted   │      │
│  │ ✅ Healthy     │ ✅ Healthy       │ features       │      │
│  └────────────────┴──────────────────┴────────────────┘      │
│                                                               │
│  ACTION BUTTONS                                               │
│  [Update UA to Dev]  [Approve Blue-Green Swap]              │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  TABS: [Versions] [Features] [Logs]                          │
│                                                               │
│  VERSIONS TAB (currently selected)                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ PRODUCTION VERSIONS                                 │    │
│  │ Active: version-2.1.5    (2026-07-25 14:30:00)      │    │
│  │ Inactive: version-2.1.0  (2026-07-20 10:15:00)      │    │
│  │                                                      │    │
│  │ STAGING VERSIONS                                    │    │
│  │ Current: alpha-version-2.1.0 (2026-07-24 09:45:00) │    │
│  │                                                      │    │
│  │ DEVELOPMENT BRANCH                                  │    │
│  │ Latest commit: abc1234 (2026-07-26 16:00:00)       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Structure

```
src/monitoring/
├── App.tsx                      # Main app component
├── pages/
│   ├── VersionsPage.tsx        # Versions tab
│   ├── FeaturesPage.tsx        # Features tab
│   └── LogsPage.tsx            # Logs tab
├── components/
│   ├── DeploymentStatus.tsx    # Status cards at top
│   ├── VersionCard.tsx         # Individual version display
│   ├── FeatureTagCard.tsx      # Feature tag display
│   ├── LogsTable.tsx           # Logs table with filters
│   ├── LogsChart.tsx           # Log volume/severity chart
│   └── ActionButtons.tsx       # UA update and swap buttons
├── api/
│   ├── github.ts               # GitHub API client
│   ├── azure.ts                # Azure Log Analytics client
│   └── types.ts                # TypeScript interfaces
├── hooks/
│   ├── useVersions.ts          # Fetch versions from GitHub tags
│   ├── useLogs.ts              # Fetch logs from Azure
│   └── useAutoRefresh.ts       # Polling hook for real-time updates
├── styles/
│   ├── App.css
│   └── theme.ts                # Tailwind or Material-UI theme
└── public/
    └── index.html
```

## Core Components

### 1. App.tsx - Main Application

```typescript
import React, { useState, useEffect } from 'react';
import { useVersions } from './hooks/useVersions';
import { useLogs } from './hooks/useLogs';
import DeploymentStatus from './components/DeploymentStatus';
import ActionButtons from './components/ActionButtons';
import VersionsPage from './pages/VersionsPage';
import FeaturesPage from './pages/FeaturesPage';
import LogsPage from './pages/LogsPage';

export default function App() {
  const [activeTab, setActiveTab] = useState<'versions' | 'features' | 'logs'>('versions');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { versions, loading: versionsLoading, error: versionsError, refetch: refetchVersions } = useVersions();
  const { logs, loading: logsLoading, refetch: refetchLogs } = useLogs();

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refetchVersions();
      refetchLogs();
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh, refetchVersions, refetchLogs]);

  return (
    <div className="monitoring-app">
      <header>
        <h1>Databricks Monitoring Dashboard</h1>
        <div className="header-controls">
          <button onClick={() => { refetchVersions(); refetchLogs(); }}>
            🔄 Refresh
          </button>
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (30s)
          </label>
        </div>
      </header>

      <main>
        {versionsError && <div className="error">{versionsError}</div>}

        <DeploymentStatus versions={versions} loading={versionsLoading} />

        <ActionButtons versions={versions} />

        <div className="tabs">
          <button
            className={activeTab === 'versions' ? 'active' : ''}
            onClick={() => setActiveTab('versions')}
          >
            Versions
          </button>
          <button
            className={activeTab === 'features' ? 'active' : ''}
            onClick={() => setActiveTab('features')}
          >
            Features
          </button>
          <button
            className={activeTab === 'logs' ? 'active' : ''}
            onClick={() => setActiveTab('logs')}
          >
            Logs
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'versions' && <VersionsPage versions={versions} loading={versionsLoading} />}
          {activeTab === 'features' && <FeaturesPage versions={versions} loading={versionsLoading} />}
          {activeTab === 'logs' && <LogsPage logs={logs} loading={logsLoading} />}
        </div>
      </main>
    </div>
  );
}
```

### 2. DeploymentStatus.tsx - Status Overview

```typescript
import React from 'react';

interface Version {
  type: 'prod-active' | 'prod-inactive' | 'staging' | 'dev';
  tag?: string;
  deployedAt?: string;
  healthy: boolean;
}

export default function DeploymentStatus({ versions, loading }: {
  versions: Version[];
  loading: boolean;
}) {
  if (loading) return <div>Loading status...</div>;

  const prodActive = versions.find(v => v.type === 'prod-active');
  const staging = versions.find(v => v.type === 'staging');
  const devFeatures = versions.filter(v => v.type === 'dev');

  return (
    <div className="deployment-status">
      <div className="status-card prod-active">
        <h3>Production (Active)</h3>
        <div className="version-number">{prodActive?.tag || 'N/A'}</div>
        <div className={`health ${prodActive?.healthy ? 'healthy' : 'unhealthy'}`}>
          {prodActive?.healthy ? '✅' : '❌'} {prodActive?.healthy ? 'Healthy' : 'Unhealthy'}
        </div>
        <div className="timestamp">{prodActive?.deployedAt || 'Unknown'}</div>
      </div>

      <div className="status-card staging">
        <h3>Staging (Alpha)</h3>
        <div className="version-number">{staging?.tag || 'N/A'}</div>
        <div className={`health ${staging?.healthy ? 'healthy' : 'unhealthy'}`}>
          {staging?.healthy ? '✅' : '❌'} {staging?.healthy ? 'Healthy' : 'Unhealthy'}
        </div>
        <div className="timestamp">{staging?.deployedAt || 'Unknown'}</div>
      </div>

      <div className="status-card dev">
        <h3>Development (Features)</h3>
        <div className="feature-count">{devFeatures.length} Unaccepted</div>
        <div className="features-list">
          {devFeatures.slice(0, 3).map((f, i) => (
            <span key={i} className="feature-tag">{f.tag}</span>
          ))}
          {devFeatures.length > 3 && <span>+{devFeatures.length - 3} more</span>}
        </div>
      </div>
    </div>
  );
}
```

### 3. FeaturesPage.tsx - Feature Tags Display

```typescript
import React, { useState } from 'react';

interface FeatureTag {
  name: string;
  createdAt: string;
  committedBy: string;
  commitMessage: string;
  accepted: boolean;
}

export default function FeaturesPage({ versions }: { versions: any[] }) {
  const [sortBy, setSortBy] = useState<'newest' | 'oldest'>('newest');

  // Extract only unaccepted feature tags (feature-* without merged-feature-* counterpart)
  const unacceptedFeatures: FeatureTag[] = versions
    .filter(v => v.type === 'feature-unaccepted')
    .map(v => ({
      name: v.tag || '',
      createdAt: v.deployedAt || '',
      committedBy: v.author || 'Unknown',
      commitMessage: v.message || '',
      accepted: false,
    }))
    .sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime();
      const dateB = new Date(b.createdAt).getTime();
      return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
    });

  return (
    <div className="features-page">
      <h2>Feature Tags Awaiting Acceptance</h2>

      <div className="controls">
        <p>
          {unacceptedFeatures.length} feature{unacceptedFeatures.length !== 1 ? 's' : ''} waiting for User Acceptance
        </p>
        <label>
          Sort by:
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
        </label>
      </div>

      <div className="features-list">
        {unacceptedFeatures.map((feature) => (
          <div key={feature.name} className="feature-card">
            <h3>{feature.name}</h3>
            <div className="meta">
              <span className="date">📅 {new Date(feature.createdAt).toLocaleString()}</span>
              <span className="author">👤 {feature.committedBy}</span>
            </div>
            <div className="message">
              <strong>Commit:</strong> {feature.commitMessage.substring(0, 100)}
              {feature.commitMessage.length > 100 ? '...' : ''}
            </div>
            <div className="actions">
              <button className="accept">✅ Accept Feature</button>
              <button className="view">📋 View Details</button>
            </div>
          </div>
        ))}
      </div>

      {unacceptedFeatures.length === 0 && (
        <div className="empty-state">
          <p>✨ All features have been accepted! Ready for pre-release?</p>
          <button className="primary">Create Pre-release</button>
        </div>
      )}
    </div>
  );
}
```

### 4. LogsPage.tsx - Logs Viewer

```typescript
import React, { useState } from 'react';

interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR';
  environment: string;
  message: string;
  source: string;
}

export default function LogsPage({ logs, loading }: {
  logs: LogEntry[];
  loading: boolean;
}) {
  const [filterLevel, setFilterLevel] = useState<'ALL' | 'ERROR' | 'WARNING' | 'INFO'>('ALL');
  const [filterEnv, setFilterEnv] = useState<'ALL' | 'DEV' | 'UA' | 'STAGING' | 'PROD'>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = logs.filter(log => {
    const levelMatch = filterLevel === 'ALL' || log.level === filterLevel;
    const envMatch = filterEnv === 'ALL' || log.environment === filterEnv;
    const searchMatch = log.message.toLowerCase().includes(searchTerm.toLowerCase());
    return levelMatch && envMatch && searchMatch;
  });

  if (loading) return <div>Loading logs...</div>;

  return (
    <div className="logs-page">
      <h2>Application Logs</h2>

      <div className="filters">
        <div className="filter-group">
          <label>
            Severity:
            <select value={filterLevel} onChange={(e) => setFilterLevel(e.target.value as any)}>
              <option value="ALL">All Levels</option>
              <option value="ERROR">Errors Only</option>
              <option value="WARNING">Warnings Only</option>
              <option value="INFO">Info Only</option>
            </select>
          </label>
        </div>

        <div className="filter-group">
          <label>
            Environment:
            <select value={filterEnv} onChange={(e) => setFilterEnv(e.target.value as any)}>
              <option value="ALL">All Environments</option>
              <option value="DEV">DEV</option>
              <option value="UA">UA</option>
              <option value="STAGING">Staging</option>
              <option value="PROD">Production</option>
            </select>
          </label>
        </div>

        <div className="filter-group">
          <label>
            Search:
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search logs..."
            />
          </label>
        </div>
      </div>

      <div className="logs-table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Level</th>
              <th>Environment</th>
              <th>Source</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map((log, i) => (
              <tr key={i} className={`level-${log.level.toLowerCase()}`}>
                <td className="timestamp">{new Date(log.timestamp).toLocaleString()}</td>
                <td className={`level ${log.level.toLowerCase()}`}>
                  {log.level === 'ERROR' && '❌'}
                  {log.level === 'WARNING' && '⚠️'}
                  {log.level === 'INFO' && 'ℹ️'}
                  {log.level}
                </td>
                <td className="environment">{log.environment}</td>
                <td className="source">{log.source}</td>
                <td className="message">{log.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredLogs.length === 0 && (
        <div className="empty-state">
          <p>No logs matching your filters</p>
        </div>
      )}
    </div>
  );
}
```

### 5. ActionButtons.tsx - Manual Triggers

```typescript
import React, { useState } from 'react';

export default function ActionButtons({ versions }: { versions: any[] }) {
  const [uaLoading, setUaLoading] = useState(false);
  const [swapLoading, setSwapLoading] = useState(false);
  const [swapApprovers, setSwapApprovers] = useState<string[]>([]);

  const handleUpdateUA = async () => {
    setUaLoading(true);
    try {
      const response = await fetch('/api/update-ua-environment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      alert(`UA environment updated to: ${data.version}`);
    } catch (error) {
      alert(`Error: ${error}`);
    } finally {
      setUaLoading(false);
    }
  };

  const handleSwapBlueGreen = async () => {
    if (swapApprovers.length < 2) {
      alert('Blue-Green swap requires at least 2 approvers');
      return;
    }

    setSwapLoading(true);
    try {
      const response = await fetch('/api/approve-blue-green-swap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approvers: swapApprovers }),
      });
      const data = await response.json();
      alert(`Blue-Green swap completed! Active version is now ${data.activeVersion}`);
    } catch (error) {
      alert(`Error: ${error}`);
    } finally {
      setSwapLoading(false);
    }
  };

  const prodActive = versions.find(v => v.type === 'prod-active');
  const prodInactive = versions.find(v => v.type === 'prod-inactive');

  return (
    <div className="action-buttons">
      <div className="button-group">
        <button
          onClick={handleUpdateUA}
          disabled={uaLoading}
          className="primary"
        >
          {uaLoading ? 'Updating...' : '🚀 Update UA to Dev'}
        </button>
        <p className="description">Deploy latest dev branch to User Acceptance environment</p>
      </div>

      <div className="button-group">
        <button
          onClick={handleSwapBlueGreen}
          disabled={swapLoading}
          className="danger"
        >
          {swapLoading ? 'Swapping...' : '🔄 Approve Blue-Green Swap'}
        </button>
        <p className="description">
          Switch active: {prodActive?.tag || 'N/A'} ↔️ {prodInactive?.tag || 'N/A'}
        </p>
        <div className="approvers">
          <p>Approvers (min 2):</p>
          {/* Approver selection UI */}
        </div>
      </div>
    </div>
  );
}
```

## API Integration

### GitHub Tags API

```typescript
// src/monitoring/api/github.ts
interface Version {
  type: 'prod-active' | 'prod-inactive' | 'staging' | 'dev';
  tag: string;
  sha: string;
  deployedAt: string;
  healthy: boolean;
}

export async function fetchVersions(): Promise<Version[]> {
  const versions: Version[] = [];

  // Fetch all tags from GitHub
  const response = await fetch('https://api.github.com/repos/levayzsombor/cs-databricks/tags');
  const tags = await response.json();

  // Parse tags and determine type
  const latestVersion = tags.find((t: any) => t.name.match(/^version-\d+\.\d+\.\d+$/));
  const latestAlpha = tags.find((t: any) => t.name.match(/^alpha-version-\d+\.\d+\.\d+$/));
  const unacceptedFeatures = tags.filter(
    (t: any) => t.name.match(/^feature-/) && !tags.some((mt: any) => mt.name === `merged-${t.name}`)
  );

  if (latestVersion) {
    versions.push({
      type: 'prod-active',
      tag: latestVersion.name,
      sha: latestVersion.commit.sha,
      deployedAt: latestVersion.commit.commit.author.date,
      healthy: true, // TODO: Check health from Azure
    });
  }

  if (latestAlpha) {
    versions.push({
      type: 'staging',
      tag: latestAlpha.name,
      sha: latestAlpha.commit.sha,
      deployedAt: latestAlpha.commit.commit.author.date,
      healthy: true,
    });
  }

  unacceptedFeatures.forEach((tag: any) => {
    versions.push({
      type: 'dev',
      tag: tag.name,
      sha: tag.commit.sha,
      deployedAt: tag.commit.commit.author.date,
      healthy: true,
    });
  });

  return versions;
}
```

### Azure Log Analytics API

```typescript
// src/monitoring/api/azure.ts
interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR';
  environment: string;
  message: string;
  source: string;
}

export async function fetchLogs(limit: number = 1000): Promise<LogEntry[]> {
  const query = `
    custom_logs_CL
    | where Level in ('INFO', 'WARNING', 'ERROR')
    | project
      Timestamp,
      Level,
      Environment,
      Message,
      Source
    | order by Timestamp desc
    | limit ${limit}
  `;

  const response = await fetch('https://api.loganalytics.io/v1/workspaces/{workspaceId}/query', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      timespan: 'P1D', // Last 24 hours
    }),
  });

  const result = await response.json();

  return result.tables[0].rows.map((row: any[]) => ({
    timestamp: row[0],
    level: row[1],
    environment: row[2],
    message: row[3],
    source: row[4],
  }));
}
```

## Deployment

### Azure Static Web Apps

```yaml
# azure-static-web-apps-*.yml
name: Deploy Monitoring Page

on:
  push:
    branches: [dev, staging, prod]
    paths:
      - src/monitoring/**

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd src/monitoring && npm install && npm run build
      - uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_TOKEN }}
          action: upload
          app_location: src/monitoring/dist
```

## Styling

### CSS/Tailwind Example

```css
/* src/monitoring/styles/App.css */

.monitoring-app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
  background: #f5f5f5;
  color: #333;
}

.deployment-status {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-card.prod-active {
  border-left: 4px solid #4caf50;
}

.status-card.staging {
  border-left: 4px solid #ff9800;
}

.status-card.dev {
  border-left: 4px solid #2196f3;
}

.health.healthy {
  color: #4caf50;
  font-weight: bold;
}

.health.unhealthy {
  color: #f44336;
  font-weight: bold;
}

.logs-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logs-table table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table tr.level-error {
  background-color: #ffebee;
}

.logs-table tr.level-warning {
  background-color: #fff3e0;
}
```

## Summary Checklist

- [ ] React components built with TypeScript
- [ ] Fetch GitHub tags API for version display
- [ ] Fetch Azure Log Analytics for log display
- [ ] Display only unaccepted feature tags (feature-* without merged-feature-*)
- [ ] Auto-refresh every 30 seconds
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Error handling with user-friendly messages
- [ ] Loading states for async operations
- [ ] Approval buttons for UA update and Blue-Green swap
- [ ] Log filtering by severity and environment
- [ ] Static deployment to Azure Storage + CDN
- [ ] No sensitive data displayed (logs filtered to Info/Warning/Error only)
