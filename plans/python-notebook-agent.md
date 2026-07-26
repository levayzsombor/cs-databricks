# Python Notebook Agent - Implementation Plan

**Agent**: Python Notebook Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 2 (Data Processing Logic)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Build Databricks notebooks that orchestrate data collection, transformation, and delivery pipelines. Notebooks should be minimal (mostly parameter passing), calling reusable Python modules from `src/`. Include clear markdown documentation, execution logging, and status reporting.

**Key Instructions to Follow**:

- databricks-python-best-practices.instructions.md
- code-review-generic.instructions.md
- qa-engineering-best-practices.instructions.md

**Copilot Skills**:

- python-fact-grounded-coding
- pylance-python-profiling

---

## Phase 2: Data Processing Logic (Week 2-3)

### Task 2.1: Country Stats Pipeline Notebook

**Objective**: Create main orchestration notebook for collecting and delivering country statistics

**Steps**:

1. Update `src/notebooks/country_stats_pipeline.ipynb`:
   - **Cell 1 (Setup)**:
     - Import logger, collectors, transformers, delivery
     - Initialize logger with execution_id (timestamp-based)
     - Log pipeline start
   - **Cell 2 (Configuration)**:
     - Parameters: target_table (default: "countries_data"), environment (dev/staging/prod)
     - Define collector parameters (API endpoints, retry count)
     - Define data quality thresholds
     - Log configuration loaded
   - **Cell 3 (Collection)**:
     - Call CountriesCollector.collect_all()
     - Call DemographicsCollector.collect_demographics()
     - Log collection metrics (records, duration, errors)
     - Handle collection failures gracefully
   - **Cell 4 (Transformation)**:
     - Call CountryTransformer.transform()
     - Call DemographicsTransformer.transform()
     - Validate output schemas
     - Log transformation metrics
   - **Cell 5 (Quality Validation)**:
     - Run data quality checks
     - Log validation results
     - Alert if quality thresholds not met
   - **Cell 6 (Delivery)**:
     - Call SparkWriter.write_to_databricks()
     - Write countries to target_table
     - Write demographics to related table
     - Log delivery metrics (rows written, duration)
   - **Cell 7 (Summary)**:
     - Report total records collected/transformed/delivered
     - Report execution time
     - Report any errors or warnings
     - Status: SUCCESS/FAILED

2. Notebook style requirements:
   - Each logical step is a separate cell
   - Clear markdown section headers before code cells
   - Code is minimal (mostly function calls)
   - All logging goes through configured logger
   - No hardcoded values (use parameters)
   - Error handling at key points
   - Results visualized where appropriate (row counts, timing)

3. Execute notebook:
   - Verify it runs without errors
   - Verify output is as expected
   - Verify all logs appear in Log Analytics
   - Verify Databricks tables are created

**Deliverables**:

- ✅ `src/notebooks/country_stats_pipeline.ipynb` - fully functional notebook
- ✅ Clear markdown cells explaining each step
- ✅ Parameters configurable at runtime
- ✅ Execution logging and status reporting

**Dependencies**:

- Databricks Agent code (collectors, transformers, delivery)
- Logging configuration
- Python modules ready and tested

**Success Criteria**:

- Notebook runs end-to-end without errors
- All logs appear in Azure Log Analytics
- Tables are created in Databricks
- Data quality checks pass
- Execution time < 5 minutes with sample data

---

### Task 2.2: Data Quality Dashboard Notebook

**Objective**: Create notebook for monitoring data quality metrics

**Steps**:

1. Create `src/notebooks/data_quality_dashboard.ipynb`:
   - **Cell 1 (Setup)**:
     - Import SQL query helpers
     - Connect to Databricks SQL endpoint
   - **Cell 2 (Load Latest Data)**:
     - Query latest records from countries table
     - Query latest records from demographics table
   - **Cell 3 (Data Freshness)**:
     - Calculate age of data (now - created_at)
     - Check if within SLA (< 24 hours)
     - Display results
   - **Cell 4 (Completeness)**:
     - Count null values per column
     - Identify missing required fields
     - Display results
   - **Cell 5 (Accuracy)**:
     - Check population values > 0
     - Check GDP values >= 0
     - Check literacy rate 0-100%
     - Display results
   - **Cell 6 (Duplicates)**:
     - Check for duplicate country codes
     - Check for duplicate records
     - Display results
   - **Cell 7 (Summary Dashboard)**:
     - Display all quality metrics in a table
     - Show pass/fail for each metric
     - Highlight failures in red
   - **Cell 8 (Recommendations)**:
     - Suggest data quality improvements
     - Link to failed records for investigation

2. Notebook style:
   - Interactive dashboard (can be scheduled or run on-demand)
   - Use Databricks SQL visualizations
   - Clear markdown explaining metrics
   - Configurable parameters (date range, thresholds)

**Deliverables**:

- ✅ `src/notebooks/data_quality_dashboard.ipynb` - data quality monitoring notebook
- ✅ Quality metrics displayed clearly
- ✅ Pass/fail indicators
- ✅ Recommendations for improvement

**Dependencies**:

- Databricks tables with country and demographics data
- Data quality validators from Databricks Agent

**Success Criteria**:

- Notebook displays all quality metrics correctly
- Can be scheduled to run daily
- Results are actionable (identify which records failed)
- Visualizations are clear and informative

---

### Task 2.3: Testing Notebook Orchestration

**Objective**: Write integration tests for notebooks

**Steps**:

1. Create `tests/integration/test_notebook_orchestration.py`:
   - Mock Databricks environment
   - Mock SparkSession with test data
   - Test country_stats_pipeline execution:
     - All collection steps execute
     - All transformation steps execute
     - All delivery steps execute
     - All logging statements work
     - Final status is SUCCESS
   - Test data_quality_dashboard:
     - All quality metrics calculated
     - Visualizations render without errors
2. Create `tests/integration/test_notebook_performance.py`:
   - Measure notebook execution time with sample data
   - Identify slow cells for optimization
   - Document performance baseline
3. Test error scenarios:
   - Collection API timeout
   - Transformation schema mismatch
   - Delivery write failure
   - Verify notebook handles errors gracefully

**Deliverables**:

- ✅ `tests/integration/test_notebook_orchestration.py` - orchestration tests
- ✅ `tests/integration/test_notebook_performance.py` - performance tests
- ✅ Performance baseline documented

**Dependencies**:

- Notebooks created (Tasks 2.1 & 2.2)
- Test fixtures for mock Spark
- QA Agent's mock fixtures

**Success Criteria**:

- All tests pass
- Notebook execution time is acceptable
- Error handling verified
- Performance baseline established

---

## Cross-Agent Dependencies

**Blocks**:

- Blocks: No direct blocks to other agents

**Depends On**:

- Databricks Agent (Python modules ready)
- QA Agent (testing infrastructure)
- CI/CD Agent (Databricks environment available)

---

## Success Criteria for Milestone 3

✅ Country stats pipeline notebook functional end-to-end  
✅ Executes all collection, transformation, delivery steps  
✅ Logs all metrics and status  
✅ Data quality dashboard shows all metrics  
✅ Notebook execution time < 5 minutes  
✅ Integration tests validate orchestration  
✅ Performance baseline documented

---

## Risks & Mitigations

| Risk                                 | Mitigation                                                  |
| ------------------------------------ | ----------------------------------------------------------- |
| Notebook has too much logic          | Keep logic minimal; move to Python modules                  |
| Performance issues with large data   | Optimize PySpark operations; test with production-like data |
| Orchestration failures hard to debug | Log every step; include stack traces in logs                |
| Notebooks don't scale to production  | Use parameters for different environments; test at scale    |

---

## Handoff Checklist

- [ ] Country stats pipeline notebook created and tested
- [ ] Data quality dashboard notebook created and tested
- [ ] All notebooks have clear markdown documentation
- [ ] Parameters are configurable at runtime
- [ ] Execution logging works end-to-end
- [ ] Status reporting shows success/failure
- [ ] Integration tests for orchestration written
- [ ] Performance baseline established
- [ ] Error handling verified
- [ ] Notebooks can be scheduled in Databricks

**When Complete**: Report back to Repository Planner with completion status and any blockers.
