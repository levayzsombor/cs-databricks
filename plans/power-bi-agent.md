# Power BI Agent - Implementation Plan

**Agent**: Power BI Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 3 (Quality & Visibility)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Design efficient data models and dashboards for Databricks integration. Create star schema data structures, optimize query performance, and build executive dashboards for country statistics and pipeline health monitoring.

**Key Instructions to Follow**:

- power-bi-databricks-integration.instructions.md
- code-review-generic.instructions.md

---

## Phase 3: Quality & Visibility (Week 3-4)

### Task 3.1: Databricks Data Source Configuration

**Objective**: Configure Databricks as Power BI data source with proper authentication

**Steps**:

1. Prepare Databricks environment:
   - Ensure Databricks SQL endpoint is running
   - Create service principal or use Azure AD authentication
   - Grant service principal read access to data tables
   - Create PAT (Personal Access Token) for Power BI if needed

2. Create Power BI Databricks connection:
   - Open Power BI Desktop
   - New data source: Databricks
   - Connection settings:
     - Server: Databricks workspace URL
     - HTTP Path: SQL endpoint path
     - Authentication: Azure AD or PAT
   - Test connection

3. Import initial tables:
   - Query: `SELECT * FROM databases_catalog.tables`
   - Import country data table
   - Import demographics data table
   - Create date dimension table (manually or auto-generate)

4. Optimize query performance:
   - Disable query folding for large tables (if needed)
   - Use DirectQuery vs Import based on data size
   - Test query performance (< 5 second load time)
   - Document query folding capabilities

**Deliverables**:

- ✅ Databricks connection configured
- ✅ Tables imported successfully
- ✅ Query performance verified
- ✅ Documentation of connection settings

**Dependencies**:

- Databricks environment with SQL endpoint
- Data tables populated by Databricks Agent
- Azure AD or PAT authentication credentials

**Success Criteria**:

- Connection test passes
- Tables load without errors
- Query performance < 5 seconds
- Can refresh data manually

---

### Task 3.2: Data Model Design

**Objective**: Design star schema data model for analytics

**Steps**:

1. Create dimension tables:
   - **Dim_Countries**:
     - CountryCode (PK): 2-char code
     - CountryName: Full name
     - Region: Geographic region
     - Area: Total area
     - Capital: Capital city

   - **Dim_Time**:
     - Date (PK): Date
     - Year: Calendar year
     - Month: Month number
     - MonthName: Month name
     - Quarter: Q1/Q2/Q3/Q4
     - DayOfWeek: Day of week name
     - WeekNumber: ISO week number

2. Create fact tables:
   - **Fact_Demographics**:
     - CountryCodeFK: Foreign key to Dim_Countries
     - DateFK: Foreign key to Dim_Time
     - GDP_USD: Gross Domestic Product
     - GDPPerCapita_USD: Per capita GDP
     - LifeExpectancy_Years: Life expectancy
     - LiteracyRate_Percent: Literacy rate (0-100)

   - **Fact_PipelineMetrics** (optional):
     - ExecutionID (PK): Unique execution ID
     - ExecutionTimestamp: When pipeline ran
     - RecordsProcessed: Total records
     - ExecutionTimeSeconds: How long it took
     - DataFreshness_Hours: Age of data
     - SuccessFlag: 0 = failed, 1 = success

3. Create relationships:
   - Fact_Demographics[CountryCodeFK] -> Dim_Countries[CountryCode]
   - Fact_Demographics[DateFK] -> Dim_Time[Date]
   - Cardinality: Many-to-one
   - Cross-filter direction: Single (fact to dimension)

4. Define calculated columns:
   - GDP_Billions = GDP_USD / 1,000,000,000
   - PopulationDescription = "High" if population > 50M, else "Low"

**Deliverables**:

- ✅ Dimension tables (Countries, Time)
- ✅ Fact tables (Demographics, PipelineMetrics)
- ✅ Relationships configured
- ✅ Calculated columns defined

**Dependencies**:

- Databricks data tables populated

**Success Criteria**:

- Star schema properly normalized
- All relationships configured correctly
- No circular relationships
- Queries execute efficiently

---

### Task 3.3: DAX Measures & KPIs

**Objective**: Define DAX measures for analytics

**Steps**:

1. Create base measures:
   - **Total_GDP** = SUM(Fact_Demographics[GDP_USD])
   - **Avg_GDP_Per_Capita** = AVERAGE(Fact_Demographics[GDPPerCapita_USD])
   - **Total_Countries** = DISTINCTCOUNT(Dim_Countries[CountryCode])
   - **Avg_Life_Expectancy** = AVERAGE(Fact_Demographics[LifeExpectancy_Years])
   - **Avg_Literacy_Rate** = AVERAGE(Fact_Demographics[LiteracyRate_Percent])

2. Create growth measures:
   - **GDP_Growth_YoY** = (Current_Year_GDP - Previous_Year_GDP) / Previous_Year_GDP
   - **Population_Growth_YoY** = (Current_Population - Previous_Population) / Previous_Population

3. Create data quality measures:
   - **Records_Count** = COUNTA(Fact_Demographics[CountryCodeFK])
   - **Data_Completeness** = (Records_With_All_Fields / Total_Records) * 100
   - **Pipeline_Success_Rate** = DIVIDE(SUM(Fact_PipelineMetrics[SuccessFlag]), COUNTA(Fact_PipelineMetrics[ExecutionID])) * 100

4. Create time-based measures:
   - **Latest_Data_Date** = MAX(Dim_Time[Date])
   - **Data_Age_Days** = TODAY() - MAX(Dim_Time[Date])
   - **On_Time_Delivery_Percent** = (On_Time_Executions / Total_Executions) * 100

**Deliverables**:

- ✅ Base measures (GDP, population, life expectancy)
- ✅ Growth measures (YoY)
- ✅ Data quality measures
- ✅ Time-based measures

**Dependencies**:

- Data model from Task 3.2

**Success Criteria**:

- All measures calculate correctly
- Measures are reusable across reports
- Performance is acceptable

---

### Task 3.4: Dashboard 1 - Country Statistics

**Objective**: Build dashboard showing country data analytics

**Steps**:

1. Create page: "Country Statistics"
   - Layout: Header with filters, main visuals, drill-through details

2. Add filter controls:
   - Region filter (dropdown)
   - Country filter (slicer)
   - Time period filter (date slicer)

3. Add key metric cards:
   - Total Countries: 195
   - Total GDP: $100 Trillion
   - Average Life Expectancy: 72 years
   - Average Literacy Rate: 85%

4. Add visualizations:
   - **Map**: Show GDP by country (color intensity)
   - **Bar Chart**: Top 10 countries by population
   - **Bar Chart**: Top 10 countries by GDP
   - **Line Chart**: Regional GDP trends over time
   - **Table**: Country details (name, GDP, population, life expectancy)

5. Add drill-through:
   - Click country -> detailed view with all metrics
   - Show region, population, GDP, life expectancy, literacy

**Deliverables**:

- ✅ "Country Statistics" page
- ✅ Filter controls
- ✅ Key metric cards
- ✅ Map, bar charts, line chart
- ✅ Drill-through to country details

**Dependencies**:

- Data model and measures from Tasks 3.2 & 3.3

**Success Criteria**:

- Dashboard loads in < 5 seconds
- Filters work correctly
- Visualizations are clear and informative
- Drill-through navigates correctly

---

### Task 3.5: Dashboard 2 - Data Pipeline Health

**Objective**: Build dashboard showing pipeline execution metrics

**Steps**:

1. Create page: "Pipeline Health"
   - Shows data pipeline execution and quality metrics

2. Add key metric cards:
   - Last Execution: Timestamp
   - Success Rate: %
   - Average Execution Time: Minutes
   - Data Freshness: Hours old

3. Add visualizations:
   - **Line Chart**: Execution time trend (last 30 days)
   - **Line Chart**: Success/failure rate trend (last 30 days)
   - **Bar Chart**: Records processed per execution
   - **Table**: Recent execution history
     - Timestamp, Status, Records, Time, Freshness

4. Add alerts/warnings:
   - Red indicator if latest execution failed
   - Yellow indicator if data > 24 hours old
   - Green indicator if all healthy

5. Add recommendations:
   - "Data is fresh" if < 1 hour old
   - "Data refresh overdue" if > 24 hours old
   - "Pipeline needs attention" if recent failures

**Deliverables**:

- ✅ "Pipeline Health" page
- ✅ Key metric cards
- ✅ Execution history visualizations
- ✅ Alerts and health indicators

**Dependencies**:

- Pipeline metrics table in Databricks
- Data model and measures

**Success Criteria**:

- Dashboard shows current pipeline status
- Trends are visible
- Alerts are clear
- Recommendations are actionable

---

### Task 3.6: Dashboard 3 - Executive Summary

**Objective**: Build high-level executive dashboard

**Steps**:

1. Create page: "Executive Summary"
   - One-page overview of key metrics

2. Add KPI cards (large, prominent):
   - **Countries Covered**: 195
   - **Total Global GDP**: $100+ Trillion
   - **Avg Life Expectancy**: 72 years
   - **Data Freshness**: 2 hours old

3. Add top-level visualizations:
   - **Map**: World GDP distribution
   - **Pie Chart**: Regional breakdown (% of global GDP)
   - **Gauge Chart**: Data quality score (0-100%)
   - **Status**: Pipeline health (Running, Success, Failed)

4. Add trends:
   - GDP growth vs last year: +2.5%
   - Population growth vs last year: +1.1%

5. Add quick insights:
   - "Top performing region: Asia (42% of global GDP)"
   - "Data updated 2 hours ago"

**Deliverables**:

- ✅ "Executive Summary" page
- ✅ Large KPI cards
- ✅ Map and distribution charts
- ✅ Quick insights

**Dependencies**:

- Measures from Task 3.3
- Data model

**Success Criteria**:

- Page loads in < 3 seconds
- Metrics are prominently displayed
- Insights are actionable

---

### Task 3.7: Report Publishing & Refresh Schedule

**Objective**: Publish reports and configure automatic refresh

**Steps**:

1. Configure refresh schedule:
   - Daily refresh at 02:00 UTC (after pipeline at 01:00 UTC)
   - Refresh should complete in < 5 minutes
   - Alert if refresh fails

2. Publish to Power BI Service:
   - Create Power BI workspace
   - Publish reports (.pbix files)
   - Configure data source credentials
   - Grant access to stakeholders

3. Configure sharing:
   - Create security groups for different access levels
   - Assign groups to workspaces
   - Document access controls

4. Create documentation:
   - How to view reports
   - How to create filtered views
   - How to export data
   - FAQ for common questions

**Deliverables**:

- ✅ Reports published to Power BI Service
- ✅ Refresh schedule configured
- ✅ Sharing and access controls set up
- ✅ User documentation

**Dependencies**:

- Power BI Service license
- Workspace configured
- Users/groups created

**Success Criteria**:

- Reports visible in Power BI Service
- Refresh completes automatically daily
- Users can access reports
- Documentation is clear

---

## Cross-Agent Dependencies

**Blocks**:

- No blocks to other agents

**Depends On**:

- Databricks Agent (data tables populated)
- CI/CD Agent (logging to track data freshness)

---

## Success Criteria for Milestone 3

✅ Databricks connection configured and tested  
✅ Star schema data model created  
✅ DAX measures for analytics defined  
✅ Country Statistics dashboard built  
✅ Pipeline Health dashboard built  
✅ Executive Summary dashboard built  
✅ Reports published to Power BI Service  
✅ Automatic daily refresh configured

---

## Risks & Mitigations

| Risk                          | Mitigation                                                 |
| ----------------------------- | ---------------------------------------------------------- |
| Databricks connection slow    | Use DirectQuery with cached aggregations; optimize queries |
| Data model too complex        | Start simple; add complexity as needed                     |
| DAX calculations slow         | Use measures instead of calculated columns; partition data |
| Reports take too long to load | Add slicers to reduce data volume; use drill-through       |
| Refresh fails frequently      | Monitor refresh logs; optimize data source queries         |

---

## Handoff Checklist

- [ ] Databricks data source connected
- [ ] Tables imported successfully
- [ ] Dimension and fact tables created
- [ ] Relationships configured correctly
- [ ] DAX measures defined and tested
- [ ] Country Statistics dashboard complete
- [ ] Pipeline Health dashboard complete
- [ ] Executive Summary dashboard complete
- [ ] Reports published to Power BI Service
- [ ] Automatic refresh configured
- [ ] User documentation written
- [ ] Access controls configured

**When Complete**: Report back to Repository Planner with completion status and any blockers.
