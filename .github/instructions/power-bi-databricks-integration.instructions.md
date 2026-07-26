---
description: 'Best practices for integrating Databricks as a data source for Power BI, including connector configuration, query optimization, and dashboard design'
applyTo: '**/*.pbix, **/*.pbit, **/power-bi/**'
---

# Power BI & Databricks Integration

Guidelines for configuring Databricks as a Power BI data source, optimizing query performance, and designing dashboards that leverage the showcase data pipeline.

## Overview

Power BI connects to Databricks to visualize country statistics and demographics data collected by the pipeline. This integration demonstrates:

- **Real-Time Data Source**: Power BI queries transformed data from Databricks tables
- **Performance Optimization**: Leveraging Databricks SQL endpoints and query caching
- **Automated Refresh**: Scheduled data refresh aligned with pipeline executions
- **Data Quality Dashboard**: Monitoring pipeline health alongside business metrics

## Data Sources

The Power BI models consume these Databricks tables:

| Table                         | Source             | Refresh Frequency |
| ----------------------------- | ------------------ | ----------------- |
| `country_stats.countries`     | REST Countries API | Daily 00:00 UTC   |
| `country_stats.demographics`  | World Bank API     | Daily 01:00 UTC   |
| `country_stats.pipeline_logs` | Application logs   | Real-time (5 min) |

## Databricks Connector Setup

### Connection String

```
Server: <databricks-host>.cloud.databricks.com
Path: /sql/1.0/endpoints/<sql-endpoint-id>
Protocol: HTTPS
Port: 443
Authentication: Personal Access Token (or Azure AD)
```

### Credential Management

**Option 1: Personal Access Token (PAT)**

```
Token Format: dapi[<scope>][<hash>]

Power BI Setup:
1. Go to Data > Get Data > Databricks
2. Enter server address: <workspace>.cloud.databricks.com
3. Use SQL endpoint ID (not cluster ID)
4. Authentication: Database > User Name/Password
5. User Name: token
6. Password: <paste your PAT>
```

**Option 2: Azure AD (Recommended)**

```
Power BI Setup:
1. Go to Data > Get Data > Databricks
2. Enter server address
3. Authentication: Microsoft Account
4. Sign in with Azure AD credentials
```

**Secrets Management**:

- Store PATs in Key Vault (if using service principal)
- Never commit credentials to Git
- Rotate tokens quarterly
- Monitor token usage in Databricks audit logs

### SQL Endpoint Configuration

```sql
-- Create a read-only SQL endpoint for Power BI
-- (Executed in Databricks workspace by admin)

CREATE SQL ENDPOINT power_bi_endpoint
CLUSTER_SIZE = "2.0 (4GB RAM, 1 core)"
AUTO_STOP_MINS = 20
WAREHOUSE_TYPE = "STANDARD"
ENABLE_RESULT_CACHING = TRUE
TAGS = ("environment" = "prod", "purpose" = "power-bi")
;
```

## Data Model Design

### Staging Tables (Optimized for Power BI)

Create a staging layer in Databricks that is optimized for Power BI queries:

```sql
-- Create materialized views for Power BI performance

-- countries_for_power_bi: Pre-aggregated and cleaned
CREATE TABLE country_stats.countries_for_power_bi AS
SELECT
  code,
  name,
  population,
  area,
  capital,
  region,
  languages,
  timezones,
  created_at,
  updated_at,
  ROW_NUMBER() OVER (PARTITION BY code ORDER BY updated_at DESC) as row_num
FROM country_stats.countries
WHERE updated_at >= DATE_SUB(CURRENT_DATE(), 30)
QUALIFY row_num = 1;

-- demographics_for_power_bi: Joined with countries for easy relationships
CREATE TABLE country_stats.demographics_for_power_bi AS
SELECT
  d.country_code,
  c.name as country_name,
  c.region,
  d.gdp_usd,
  d.gdp_per_capita_usd,
  d.life_expectancy_years,
  d.literacy_rate_percent,
  d.updated_at,
  ROW_NUMBER() OVER (PARTITION BY d.country_code ORDER BY d.updated_at DESC) as row_num
FROM country_stats.demographics d
JOIN country_stats.countries c ON d.country_code = c.code
QUALIFY row_num = 1;

-- Create indexes for faster queries
CREATE INDEX idx_countries_region ON country_stats.countries_for_power_bi (region);
CREATE INDEX idx_demographics_country ON country_stats.demographics_for_power_bi (country_code);
```

### Power BI Model Structure

```
Power BI Model
├── Dimension Tables
│   ├── Dim_Countries
│   │   ├── CountryCode (PK)
│   │   ├── CountryName
│   │   ├── Region
│   │   ├── Area
│   │   └── Capital
│   ├── Dim_Time
│   │   ├── Date (PK)
│   │   ├── Year
│   │   ├── Month
│   │   ├── Quarter
│   │   └── DayOfWeek
│   └── Dim_Metrics
│       ├── MetricID (PK)
│       ├── MetricName
│       └── MetricType
│
└── Fact Tables
    ├── Fact_Demographics
    │   ├── CountryCode (FK to Dim_Countries)
    │   ├── Date (FK to Dim_Time)
    │   ├── GDP_USD
    │   ├── GDPPerCapita_USD
    │   ├── LifeExpectancy_Years
    │   └── LiteracyRate_Percent
    │
    └── Fact_PipelineMetrics
        ├── ExecutionID (PK)
        ├── Date (FK to Dim_Time)
        ├── EnvironmentName
        ├── RecordsProcessed
        ├── RecordsFailed
        ├── ExecutionTimeSeconds
        └── DataFreshness_Hours
```

## DAX Measures & Calculations

### Calculated Columns

```dax
// Dim_Countries
Country_Key = [CountryCode] & "-" & FORMAT([CountryCode], "000")

// Fact_Demographics
GDP_Category =
  SWITCH(TRUE(),
    [GDP_USD] > 10000000000000, "Very Large",
    [GDP_USD] > 1000000000000, "Large",
    [GDP_USD] > 100000000000, "Medium",
    [GDP_USD] > 10000000000, "Small",
    "Very Small"
  )

LifeExpectancy_Category =
  SWITCH(TRUE(),
    [LifeExpectancy_Years] >= 80, "Very High",
    [LifeExpectancy_Years] >= 75, "High",
    [LifeExpectancy_Years] >= 65, "Medium",
    "Low"
  )
```

### Key Measures

```dax
// Revenue & Economic Measures
Total_GDP = SUM([GDP_USD])
Avg_GDP_Per_Capita = AVERAGE([GDPPerCapita_USD])
GDP_Growth = DIVIDE([Total_GDP], CALCULATE([Total_GDP], DATEADD(Dim_Time[Date], -1, YEAR)), 0)

// Population Metrics
Total_Population = SUM(Dim_Countries[Population])
Avg_Life_Expectancy = AVERAGE([LifeExpectancy_Years])
Weighted_Literacy_Rate = SUMPRODUCT(Dim_Countries[Population], [LiteracyRate_Percent]) / [Total_Population]

// Pipeline Health Metrics
Total_Records_Processed = SUM([RecordsProcessed])
Pipeline_Success_Rate = DIVIDE(
  [Total_Records_Processed] - SUM([RecordsFailed]),
  [Total_Records_Processed],
  0
)
Avg_Execution_Time = AVERAGE([ExecutionTimeSeconds])
Data_Freshness_Hours = MIN([DataFreshness_Hours])

// Performance Indicators
On_Time_Delivery_Percent =
  DIVIDE(
    COUNTROWS(FILTER(Fact_PipelineMetrics, [ExecutionTimeSeconds] < 300)),
    COUNTA(Fact_PipelineMetrics[ExecutionID]),
    0
  ) * 100
```

## Dashboard Design

### Dashboard 1: Country Statistics

**Purpose**: Show global country data at a glance

**Pages/Views**:

1. **Overview**
   - World map with population by country
   - Top 10 countries by population
   - Top 10 countries by GDP
   - Average life expectancy by region

2. **Regional Analysis**
   - Region selector (slicer)
   - Regional GDP distribution (pie chart)
   - Average life expectancy by region (bar chart)
   - Literacy rate distribution (scatter plot)

3. **Country Details**
   - Country selector (slicer)
   - Key metrics cards (GDP, population, life expectancy, literacy)
   - Trends (30-day history)
   - Comparison to regional average

**Visuals**:

- Maps: Choropleth by population/GDP
- Tables: Top/bottom countries by metric
- Charts: Line, bar, scatter for trends and distributions
- Cards: KPI summary

### Dashboard 2: Data Pipeline Health

**Purpose**: Monitor Databricks pipeline execution and data quality

**Pages/Views**:

1. **Pipeline Status**
   - Last execution timestamp
   - Success/failure count (last 30 days)
   - Execution time trend
   - Records processed trend

2. **Data Quality**
   - Data freshness (hours old)
   - Row counts by table
   - Null/validation errors
   - Duplicate detection

3. **Environment Health**
   - DEV, UA, Staging, Prod status indicators
   - Resource utilization
   - Error rate by environment

**Visuals**:

- Gauge: Data freshness (hours)
- Card: Last execution status
- Line chart: Success rate over time
- Bar chart: Records processed per execution
- Table: Error log summary

### Dashboard 3: Executive Summary

**Purpose**: High-level business and operational overview

**Pages/Views**:

1. **Global Snapshot**
   - Total countries: 195
   - Total GDP: $XX trillion
   - Average life expectancy: XX years
   - Data last refreshed: [timestamp]

2. **Key Trends**
   - GDP growth quarter-over-quarter
   - Population growth
   - Life expectancy improvements
   - Literacy rate changes

**Visuals**:

- KPI cards with trend indicators
- Waterfall chart: GDP changes
- Heat map: Regional performance

## Query Performance Optimization

### Best Practices for Power BI Queries

```sql
-- ❌ BAD: Unnecessary columns, no filtering, complex joins
SELECT *
FROM country_stats.countries c
JOIN country_stats.demographics d ON c.code = d.country_code
JOIN country_stats.pipeline_logs p ON d.updated_at = p.timestamp
WHERE YEAR(c.created_at) = YEAR(CURRENT_DATE())

-- ✅ GOOD: Only needed columns, pre-filtered, simple joins
SELECT
  c.code,
  c.name,
  c.population,
  d.gdp_usd,
  d.life_expectancy_years,
  d.updated_at
FROM country_stats.countries_for_power_bi c
LEFT JOIN country_stats.demographics_for_power_bi d
  ON c.code = d.country_code
WHERE d.updated_at >= DATE_SUB(CURRENT_DATE(), 30)
```

### Query Folding (Push to Databricks)

Ensure queries are pushed down to Databricks, not executed in Power BI:

```dax
// ✅ GOOD: Query folding possible (filter in Databricks)
Fact_Demographics_Filtered =
  FILTER(
    SUMMARIZE(
      'Fact_Demographics',
      'Dim_Countries'[Region],
      "Avg_Life_Exp", AVERAGE('Fact_Demographics'[LifeExpectancy_Years])
    ),
    [Avg_Life_Exp] > 75
  )

// ❌ BAD: No query folding (calculated in Power BI)
Fact_Demographics_Filtered_Bad =
  ADDCOLUMNS(
    'Fact_Demographics',
    "Custom_Calc", RAND()  // Random function breaks folding
  )
```

### Caching Strategy

```sql
-- Enable result caching on SQL endpoint
ALTER SQL ENDPOINT power_bi_endpoint
SET ENABLE_RESULT_CACHING = TRUE
SET RESULT_CACHING_TTL_SECONDS = 3600  -- 1 hour
```

## Data Refresh Schedule

### Power BI Refresh Configuration

**Scheduled Refresh**:

- Frequency: Daily
- Time: 02:00 UTC (after Databricks pipeline completes at 01:00)
- Retry: Up to 2 times on failure
- Notify on failure: Yes

**Configuration in Power BI**:

```
1. Go to Datasets > Settings
2. Data source credentials > Edit credentials
3. Select SQL Server credentials (PAT or AD)
4. Scheduled refresh > On
5. Refresh frequency: Daily
6. Refresh time: 02:00 UTC
7. Send refresh failure notification to: [email]
```

### Incremental Refresh (Optional)

For large datasets (> 1GB), implement incremental refresh:

```dax
// Add to Fact_Demographics table
RangeStart = DATE(2024, 1, 1)
RangeEnd = TODAY()

// Apply filter in Power BI
[Updated_At] >= RangeStart AND [Updated_At] < RangeEnd
```

## Row-Level Security (RLS)

For multi-tenant scenarios, implement RLS:

```dax
// Create security roles per region
Role: Region_Americas
DAX Filter: 'Dim_Countries'[Region] IN {"North America", "South America", "Central America"}

Role: Region_Europe
DAX Filter: 'Dim_Countries'[Region] = "Europe"

// Map users to roles in Power BI Service Admin Portal
```

## Monitoring & Troubleshooting

### Monitoring Refresh Success

```sql
-- Query Databricks audit logs for Power BI queries
SELECT
  timestamp,
  user_identity.email as user_email,
  endpoint_id,
  query_string,
  execution_time_ms,
  rows_produced,
  exception
FROM system.access.audit
WHERE user_identity.email = '[power-bi-service-principal]'
  AND timestamp >= DATE_SUB(CURRENT_DATE(), 7)
ORDER BY timestamp DESC;
```

### Common Issues & Solutions

| Issue                  | Cause                | Solution                                             |
| ---------------------- | -------------------- | ---------------------------------------------------- |
| Slow refresh (>30 min) | Large table scan     | Pre-aggregate in Databricks, use incremental refresh |
| "Connection failed"    | Expired PAT          | Rotate PAT, update Power BI credentials              |
| Missing data           | Data pipeline failed | Check pipeline logs in Monitoring dashboard          |
| High query cost        | Unoptimized queries  | Enable query folding, reduce columns, add filters    |

## Security Best Practices

- **Never hardcode credentials** in Power BI files
- **Use service principal** for automated refreshes
- **Enable encryption** in transit (HTTPS) and at rest
- **Rotate PATs** quarterly
- **Limit read-only access** for Power BI to designated tables
- **Audit data access** via Databricks audit logs
- **Implement RLS** for sensitive data by region/department

## Deployment & Versioning

### Git Management

Store Power BI files in Git (as source control):

```
/power-bi/
├── Dashboards/
│   ├── Country_Statistics.pbix
│   └── Pipeline_Health.pbix
├── Templates/
│   └── Showcase_Template.pbit
└── DAX/
    └── Measures.dax
```

### Version Control

- Export reports as Power BI Templates (`.pbit`) for version control
- Include metadata: creation date, author, refresh schedule
- Document DAX measures and relationships

## Checklist

- [ ] Databricks SQL endpoint created and optimized
- [ ] Power BI service connected with Azure AD or PAT
- [ ] Staging tables created in Databricks (optimized for BI queries)
- [ ] Data model designed with proper relationships
- [ ] DAX measures created for KPIs
- [ ] Dashboards built with visualizations
- [ ] Scheduled refresh configured (daily at 02:00 UTC)
- [ ] Query performance validated (< 30 seconds for refresh)
- [ ] RLS implemented if needed
- [ ] Monitoring & alerting configured for refresh failures
- [ ] Documentation updated with data dictionary
- [ ] Training completed for dashboard users

---

## Related Documentation

- **Databricks Connector**: https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-connect-databricks
- **DAX Function Reference**: https://dax.guide/
- **Power BI Performance**: https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization
