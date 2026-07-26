# QA Agent (Ivy) - Implementation Plan

**Agent**: QA Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 1 (Foundation) & 3 (Validation & Quality)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Write comprehensive unit tests, schema validation tests, and data quality tests for Databricks pipelines. Achieve > 80% test coverage with 100% mocking of external dependencies (APIs, database, Spark). Write clear test cases following Given-When-Then pattern.

**Key Instructions to Follow**:

- qa-engineering-best-practices.instructions.md
- database-schema-validation-testing.instructions.md
- code-review-generic.instructions.md

**Copilot Skills**:

- python-fact-grounded-coding

---

## Phase 1: Foundation & Infrastructure (Week 1-2)

### Task 1.1: Test Infrastructure & Fixtures

**Objective**: Set up pytest framework with reusable fixtures and mocks

**Steps**:

1. Create `tests/conftest.py`:
   - Pytest configuration and shared fixtures
   - Mock Spark fixtures (MagicMock SparkSession, DataFrame)
   - Mock API response fixtures
   - Database connection mocks
   - Logging setup for tests
2. Create `tests/fixtures/mock_data.py`:
   - Generate sample country data (list of dicts)
   - Generate sample demographics data
   - Generate sample API responses (REST Countries, World Bank format)
   - Parameterized fixtures for different data scenarios
   - Edge case data (empty, null, invalid values)
3. Create `tests/fixtures/mock_spark.py`:
   - MagicMock SparkSession with typical methods
   - MagicMock DataFrame with schema, collect, write
   - Helper functions for creating test DataFrames
   - Mock Spark exceptions for error testing
4. Create `tests/conftest.py` pytest plugins:
   - Logging capture for test validation
   - Coverage reporting setup
   - Markers for unit/integration/schema tests
5. Write tests for test infrastructure:
   - Verify mocks work as expected
   - Test fixture data quality
   - Test coverage reporting

**Deliverables**:

- ✅ `tests/conftest.py` with shared configuration
- ✅ `tests/fixtures/mock_data.py` with sample data
- ✅ `tests/fixtures/mock_spark.py` with Spark mocks
- ✅ Pytest configuration for coverage and markers

**Dependencies**:

- pytest, pytest-cov packages in pyproject.toml
- Databricks Agent code available for testing

**Success Criteria**:

- Fixtures can be imported in any test
- Mocks work without real API/DB calls
- Coverage reporting works
- Tests run in < 5 seconds

---

### Task 1.2: Unit Tests for Core Modules

**Objective**: Write 100% mocked unit tests for logging, models, clients, and database layers

**Steps**:

1. Create `tests/unit/test_logging_config.py`:
   - Test logger creation and configuration
   - Test log levels (DEBUG, INFO, WARNING, ERROR)
   - Test JSON formatting for Log Analytics
   - Test environment-aware configuration
2. Create `tests/unit/test_models.py`:
   - Test Pydantic Country model validation
     - Valid data creates model successfully
     - Invalid data raises ValidationError
     - Type conversion works (string to int)
     - Optional fields are optional
     - Required fields are required
   - Test Demographics model validation
   - Test error messages are clear
3. Create `tests/unit/test_clients.py`:
   - Test REST Countries client with mocked responses
     - get_all_countries() returns list of Country objects
     - get_by_code() returns single Country object
     - 404 error handled gracefully
     - Retry logic works (3 attempts with backoff)
   - Test World Bank client similarly
   - Test rate limiting detection (429 responses)
   - Test logging of requests/responses
4. Create `tests/unit/test_database.py`:
   - Test SparkSession wrapper
   - Test connection error handling
   - Test schema validation
     - Schema matches expected structure
     - Column types are correct
     - Nullable constraints enforced
     - Mismatches raise clear errors
5. Test coverage:
   - Use pytest-cov to track coverage
   - Aim for > 80% coverage overall
   - 100% coverage on critical paths (validation, error handling)

**Deliverables**:

- ✅ `tests/unit/test_logging_config.py` with logger tests
- ✅ `tests/unit/test_models.py` with Pydantic tests
- ✅ `tests/unit/test_clients.py` with API client tests
- ✅ `tests/unit/test_database.py` with database tests
- ✅ Coverage report showing > 80% coverage

**Dependencies**:

- Databricks Agent code available
- Pytest fixtures (Task 1.1)

**Success Criteria**:

- All tests pass
- All external dependencies are mocked
- No real API or database calls
- Coverage > 80%
- Tests run in < 10 seconds

---

### Task 1.3: Schema Validation Tests

**Objective**: Write tests to validate Databricks schema compliance

**Steps**:

1. Create `tests/schema/test_country_schema.py`:
   - Test COUNTRY_SCHEMA definition:
     - code: StringType, not nullable, length 2
     - name: StringType, not nullable
     - population: LongType, not nullable, >= 0
     - area: DoubleType, nullable, >= 0
     - capital: StringType, nullable
     - region: StringType, not nullable
     - created_at: TimestampType, not nullable
   - Test schema validation function:
     - Valid DataFrame passes validation
     - Missing column raises error
     - Wrong type raises error
     - Nullable constraint violation detected
2. Create `tests/schema/test_demographics_schema.py`:
   - Similar tests for demographics table schema
   - Validate numeric ranges (GDP >= 0, literacy 0-100, life_expectancy > 0)
3. Create `tests/schema/test_schema_evolution.py`:
   - Test schema changes over time
   - New columns can be added
   - Old columns can be deprecated (with warnings)
4. Create `tests/database/test_table_structure.py`:
   - Test that Databricks table structure matches schema
   - Test primary keys and unique constraints
   - Test foreign key relationships (if applicable)

**Deliverables**:

- ✅ `tests/schema/test_country_schema.py` with schema validation
- ✅ `tests/schema/test_demographics_schema.py` with schema validation
- ✅ `tests/schema/test_schema_evolution.py` for schema changes
- ✅ `tests/database/test_table_structure.py` for table validation

**Dependencies**:

- Database schemas (Task 1.4 of Databricks Agent)
- Spark mock fixtures (Task 1.1)

**Success Criteria**:

- Schema validation catches all schema errors
- Schema evolution is handled gracefully
- Tests run with mocked Spark
- Tests document expected schema

---

## Phase 3: Validation & Quality (Week 3-4)

### Task 3.1: Data Transformation Tests

**Objective**: Write tests for data collection and transformation logic

**Steps**:

1. Create `tests/unit/test_collectors.py`:
   - Test CountriesCollector:
     - collect_all() parses API response correctly
     - collect_by_code() finds specific country
     - Handles API errors gracefully
     - Logs collection metrics
   - Test DemographicsCollector similarly
   - Test with mocked API responses
   - Verify Pydantic models created successfully
2. Create `tests/unit/test_transformers.py`:
   - Test CountryTransformer:
     - Transforms Country objects to Spark DataFrame
     - Output schema matches expected
     - Metrics are calculated correctly
     - Errors are logged
   - Test with mocked Spark DataFrame
   - Test with edge case data (empty, nulls, invalid values)
3. Create `tests/unit/test_delivery.py`:
   - Test SparkWriter:
     - write_to_databricks() creates table if not exists
     - Schema validation runs before write
     - Row count > 0 validated
     - Metrics are logged
   - Test error handling:
     - Duplicate key error caught
     - Schema mismatch error caught
     - Write failure logged
4. Test coverage:
   - Aim for 100% coverage on critical paths
   - All error scenarios tested

**Deliverables**:

- ✅ `tests/unit/test_collectors.py` with collector tests
- ✅ `tests/unit/test_transformers.py` with transformer tests
- ✅ `tests/unit/test_delivery.py` with delivery tests
- ✅ Coverage report showing > 80% overall

**Dependencies**:

- Collectors, transformers, delivery modules (Phase 2 of Databricks Agent)
- Test fixtures and mocks (Task 1.1)

**Success Criteria**:

- All transformation logic tested
- All external dependencies mocked
- Error scenarios covered
- Coverage > 80%

---

### Task 3.2: Data Quality Tests

**Objective**: Write tests to validate data quality metrics

**Steps**:

1. Create `tests/quality/test_data_quality.py`:
   - Test data freshness:
     - Data age is within SLA (e.g., < 24 hours old)
     - Timestamp validation
   - Test data completeness:
     - Required fields are not null
     - All expected records present
   - Test data accuracy:
     - Numeric values in valid ranges
     - String values properly formatted
     - No duplicate primary keys
2. Create `tests/quality/test_country_data.py`:
   - Test country data quality:
     - Population > 0
     - Area >= 0 (or null)
     - Country code is 2 chars
     - Country name not empty
3. Create `tests/quality/test_demographics_data.py`:
   - Test demographics data quality:
     - GDP >= 0
     - GDP per capita >= 0
     - Life expectancy > 0 and < 150
     - Literacy rate 0-100%
4. Create data quality validator:
   - Reusable validation functions
   - Clear error messages
   - Logging of quality metrics
5. Integrate with pipeline:
   - Run quality checks after transformation
   - Log quality report (pass/fail per metric)
   - Alert if quality fails

**Deliverables**:

- ✅ `tests/quality/test_data_quality.py` with quality validators
- ✅ `tests/quality/test_country_data.py` with country validation
- ✅ `tests/quality/test_demographics_data.py` with demographics validation
- ✅ Data quality validator in `src/data/validators.py`

**Dependencies**:

- Pydantic models and transformers (Databricks Agent Phase 1 & 2)

**Success Criteria**:

- Data quality checks validate all metrics
- Clear failure messages
- Validation is logged
- Tests document expected data quality

---

### Task 3.3: Integration Tests

**Objective**: Write end-to-end tests for full pipeline

**Steps**:

1. Create `tests/integration/test_pipeline_end_to_end.py`:
   - Test full pipeline with mocked APIs:
     - Collect data from mocked REST Countries API
     - Collect data from mocked World Bank API
     - Transform to Spark DataFrame
     - Validate schema
     - Write to mocked Databricks table
   - Verify complete flow works
   - Log metrics at each step
2. Create `tests/integration/test_error_handling.py`:
   - Test pipeline resilience:
     - API timeout handled gracefully
     - Partial data processed (skip failed records)
     - Schema validation prevents bad writes
     - Errors are logged with context
3. Create performance tests:
   - Measure collection time (mock API responses)
   - Measure transformation time (with sample data)
   - Measure write time (mocked Databricks)
   - Document performance expectations

**Deliverables**:

- ✅ `tests/integration/test_pipeline_end_to_end.py` with full pipeline tests
- ✅ `tests/integration/test_error_handling.py` with resilience tests
- ✅ Performance metrics documented

**Dependencies**:

- All Databricks Agent code (Phases 1 & 2)
- Test fixtures and mocks (Task 1.1)

**Success Criteria**:

- Full pipeline runs end-to-end
- All external dependencies mocked
- Errors are handled gracefully
- Performance is acceptable (< 1 minute for full pipeline with sample data)

---

## Cross-Agent Dependencies

**Blocks**:

- Blocks: No other agents (QA runs after code is written)

**Depends On**:

- Databricks Agent (code to test)
- CI/CD Specialist Agent (logging configuration)

---

## Success Criteria for Milestone 3

✅ Test infrastructure set up with pytest and fixtures  
✅ Unit tests for all modules (> 80% coverage)  
✅ Schema validation tests working  
✅ Data transformation tests passing  
✅ Data quality tests defined and passing  
✅ Integration tests for full pipeline  
✅ All tests use 100% mocks (no real API/DB)  
✅ Test runs complete in < 30 seconds  
✅ Coverage report shows > 80% coverage

---

## Risks & Mitigations

| Risk                                         | Mitigation                                                      |
| -------------------------------------------- | --------------------------------------------------------------- |
| Mocks don't accurately reflect real behavior | Review mocks regularly; validate against real APIs periodically |
| Tests are brittle (fail on small changes)    | Use Given-When-Then pattern; avoid implementation details       |
| Test coverage is low                         | Use coverage.py to track; mark untestable code                  |
| Tests are slow                               | Use fixtures to share expensive operations; profile slow tests  |

---

## Handoff Checklist

- [ ] Test infrastructure configured (pytest, fixtures, mocks)
- [ ] Unit tests for all modules (logging, models, clients, database)
- [ ] Schema validation tests for all tables
- [ ] Data transformation tests (collectors, transformers, delivery)
- [ ] Data quality tests with validators
- [ ] Integration tests for full pipeline
- [ ] All tests use 100% mocks
- [ ] Coverage report shows > 80%
- [ ] Tests run in < 30 seconds
- [ ] Performance metrics documented

**When Complete**: Report back to Repository Planner with completion status and any blockers.
