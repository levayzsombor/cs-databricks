# Databricks Agent - Implementation Plan

**Agent**: Databricks Agent  
**Milestone**: 3 - Agent-Specific Plans & Implementation  
**Phase**: 1 (Foundation) & 2 (Data Processing Logic)  
**Status**: In Progress  
**Last Updated**: 2026-07-26

---

## Responsibilities Summary

Build core data collection, transformation, and delivery pipelines using PySpark, Pydantic, and structured logging. Write production-grade Python code with type safety (typy), comprehensive tests (pytest + mocks), and comprehensive documentation.

**Key Instructions to Follow**:

- databricks-python-best-practices.instructions.md
- code-review-generic.instructions.md
- context-engineering.instructions.md
- qa-engineering-best-practices.instructions.md

**Copilot Skills**:

- python-fact-grounded-coding
- pylance-refactoring
- pylance-python-profiling

---

## Phase 1: Foundation & Infrastructure (Week 1-2)

### Task 1.1: Logging Framework Setup

**Objective**: Implement structured logging with loguru for all Python modules

**Steps**:

1. Create `src/logging_config.py`:
   - Configure loguru with timestamp, severity (DEBUG/INFO/WARNING/ERROR)
   - Set sink to stdout (Info/Warning/Error) and file (Debug local only)
   - Add Azure Log Analytics HTTP sink for production environments
   - Environment-aware configuration (DEV/UA/Staging/Prod)
2. Create `LoggerFactory` utility:
   - Get logger by module name
   - Add contextual information (agent, environment, execution_id)
   - Ensure all logs are JSON-serializable for Log Analytics
3. Apply logging to all modules:
   - API client calls (request/response)
   - Data transformation steps (input/output shapes)
   - Database operations (connection, writes, errors)
   - Pipeline execution (start/end/duration/status)
4. Test logging output:
   - Verify timestamps and severity levels
   - Confirm JSON format for Azure Log Analytics
   - Verify no PII in logs

**Deliverables**:

- ✅ `src/logging_config.py` with loguru configuration
- ✅ `LoggerFactory` class for consistent logger creation
- ✅ Logging applied to all existing modules
- ✅ Test verifying log format and severity levels

**Dependencies**:

- loguru package installed in pyproject.toml
- Azure Log Analytics workspace ready (from CI/CD Agent)

**Success Criteria**:

- Logger can be imported in any module
- Logs include timestamp and severity
- JSON format compatible with Log Analytics
- Debug logs only show locally, not in production

---

### Task 1.2: Pydantic Data Models

**Objective**: Define type-safe data models for country data, API responses, and database records

**Steps**:

1. Create `src/models/` folder with:
   - `country.py`: Country domain model
     - Fields: code (2-char), name, population, area, capital, region, created_at
     - Validation: code length, name not empty, population >= 0, area >= 0
     - Type hints on all fields
   - `demographics.py`: Demographics data model
     - Fields: country_code, gdp_usd, gdp_per_capita_usd, life_expectancy_years, literacy_rate_percent, updated_at
     - Validation: codes valid, numeric ranges valid
   - `api_response.py`: Response models from external APIs
     - REST Countries response schema
     - World Bank API response schema
     - Error response schemas
   - `base.py`: Base model with common validation logic
2. Add field validators:
   - Trim/validate strings
   - Validate numeric ranges
   - Ensure required fields present
   - Convert data types as needed
3. Add error handling:
   - Raise ValidationError with clear messages
   - Log validation failures
   - Include field names in error messages
4. Write tests:
   - Test valid data creates model successfully
   - Test invalid data raises ValidationError
   - Test optional fields work correctly
   - Test type conversions

**Deliverables**:

- ✅ `src/models/` folder with all domain models
- ✅ Field validators and error handling
- ✅ Tests for all models (100% coverage)
- ✅ Type hints on all public APIs

**Dependencies**:

- pydantic and typy packages in pyproject.toml
- Logging configured (Task 1.1)

**Success Criteria**:

- All models have type hints and validation
- Invalid data raises clear errors
- Models are JSON-serializable
- Tests pass with > 80% coverage

---

### Task 1.3: API Client Framework

**Objective**: Create reusable HTTP client for external API integrations

**Steps**:

1. Create `src/clients/base.py`:
   - Base HTTP client class with:
     - Session management and connection pooling
     - Retry logic with exponential backoff (3 retries, 1s/2s/4s delays)
     - Rate limiting support (detect 429, wait before retry)
     - Request/response logging (URL, method, status, timing)
     - Error handling and exceptions
   - Dependency injection for testability
2. Create `src/clients/rest_countries.py`:
   - REST Countries API client
   - Methods: get_all_countries(), get_country_by_code(code)
   - Response parsing and validation against Pydantic models
   - Error handling for 404, 500, rate limits
3. Create `src/clients/world_bank.py`:
   - World Bank API client
   - Methods: get_demographics(country_code), get_indicator(code, year)
   - Implement pagination handling
   - Response parsing and validation
4. Write tests:
   - Mock HTTP responses for both clients
   - Test retry logic works
   - Test rate limiting detection
   - Test error handling and logging

**Deliverables**:

- ✅ `src/clients/base.py` with reusable HTTP client
- ✅ `src/clients/rest_countries.py` with API methods
- ✅ `src/clients/world_bank.py` with API methods
- ✅ Tests with 100% mocks (no real API calls)

**Dependencies**:

- requests and httpx packages
- Pydantic models (Task 1.2)
- Logging configured (Task 1.1)

**Success Criteria**:

- All API calls are mocked in tests
- Retry logic works for transient failures
- Rate limiting is detected and handled
- Logs include request/response details

---

### Task 1.4: Database Layer & Schemas

**Objective**: Define Databricks/Spark schemas and connection utilities

**Steps**:

1. Create `src/database/schemas.py`:
   - Define PySpark StructType for countries:
     - code: StringType, nullable=false, unique
     - name: StringType, nullable=false
     - population: LongType, nullable=false
     - area: DoubleType, nullable=true
     - capital: StringType, nullable=true
     - region: StringType, nullable=false
     - created_at: TimestampType, nullable=false
   - Define PySpark StructType for demographics:
     - country_code: StringType, nullable=false, FK to countries
     - gdp_usd: DoubleType, nullable=false
     - gdp_per_capita_usd: DoubleType, nullable=false
     - life_expectancy_years: DoubleType, nullable=false
     - literacy_rate_percent: DoubleType, nullable=false
     - updated_at: TimestampType, nullable=false
2. Create `src/database/connection.py`:
   - SparkSession wrapper for testability
   - Connection parameters from environment variables
   - Health check method (simple query)
   - Error handling for connection failures
3. Create `src/database/validators.py`:
   - Schema validation functions
   - Validate DataFrame schema matches expected
   - Check column types and nullability
   - Detect schema mismatches early
4. Write tests:
   - Mock SparkSession for connection tests
   - Test schema validation
   - Test error handling

**Deliverables**:

- ✅ `src/database/schemas.py` with Spark schemas
- ✅ `src/database/connection.py` with connection wrapper
- ✅ `src/database/validators.py` with schema validators
- ✅ Tests with mocked Spark (no real DB required)

**Dependencies**:

- pyspark package
- Logging configured (Task 1.1)

**Success Criteria**:

- Schemas are well-documented with types and constraints
- Connection wrapper handles errors gracefully
- Schema validation catches mismatches
- Tests don't require actual Databricks instance

---

## Phase 2: Data Processing Logic (Week 2-3)

### Task 2.1: Data Collection Module

**Objective**: Build collectors for REST Countries and World Bank APIs

**Steps**:

1. Create `src/data/collectors/rest_countries.py`:
   - `CountriesCollector` class:
     - `collect_all()`: Fetch all countries
     - `collect_by_code(code)`: Fetch specific country
     - Handle pagination if needed
     - Parse responses into Pydantic Country models
     - Log collection metrics (count, duration)
     - Error handling for API failures
2. Create `src/data/collectors/world_bank.py`:
   - `DemographicsCollector` class:
     - `collect_demographics(country_code, years)`: Fetch demographics
     - Parse World Bank indicators into Pydantic Demographics models
     - Handle missing data gracefully
     - Log collection metrics
3. Create `src/data/collectors/base.py`:
   - Base collector interface
   - Common collection methods
   - Metric tracking (records collected, errors, duration)
4. Write tests:
   - Mock API responses
   - Test successful collection
   - Test error handling and retries
   - Verify Pydantic validation

**Deliverables**:

- ✅ `src/data/collectors/` with REST Countries and World Bank collectors
- ✅ Collectors handle errors and log metrics
- ✅ Tests with mocked API responses (100% coverage)

**Dependencies**:

- API clients (Task 1.3)
- Pydantic models (Task 1.2)
- Logging (Task 1.1)

**Success Criteria**:

- Collectors fetch data and parse to Pydantic models
- No real API calls in tests
- Error handling works for network failures
- Metrics are logged for each collection

---

### Task 2.2: Data Transformation Module

**Objective**: Transform raw API data using PySpark

**Steps**:

1. Create `src/data/transformers/country_transform.py`:
   - `CountryTransformer` class:
     - `transform(api_countries)`: Transform API response to Spark DataFrame
     - Join multiple data sources if needed
     - Validate schema matches expected
     - Add metadata (processing timestamp, data source, version)
     - Log transformation metrics (input/output row counts, errors)
2. Implement transformations:
   - Normalize country codes (uppercase, validate length)
   - Clean strings (trim, normalize case)
   - Validate numeric fields (no negative values)
   - Handle missing data (log, use defaults, or skip)
   - Enrich data if multiple sources
3. PySpark best practices:
   - Keep data distributed (avoid .collect())
   - Use lazy evaluation
   - Validate schema before write
   - Cache if reused
4. Write tests:
   - Create small test DataFrames
   - Mock Spark operations
   - Test transformation logic
   - Verify output schema

**Deliverables**:

- ✅ `src/data/transformers/country_transform.py` with PySpark logic
- ✅ Tests with mocked DataFrames
- ✅ Transformation metrics logged

**Dependencies**:

- PySpark package
- Pydantic models (Task 1.2)
- Logging (Task 1.1)
- Database schemas (Task 1.4)

**Success Criteria**:

- Transformations use PySpark efficiently
- Output schema matches expected
- Tests validate transformation logic
- Metrics are logged

---

### Task 2.3: Data Delivery Module

**Objective**: Write validated data to Databricks

**Steps**:

1. Create `src/data/delivery/spark_writer.py`:
   - `SparkWriter` class:
     - `write_to_databricks(df, table_name)`: Write DataFrame to table
     - Validate schema before write
     - Handle schema evolution (if schema changes)
     - Create table if not exists
     - Log write metrics (rows, duration, errors)
     - Error handling for write failures
2. Implement validation:
   - Call schema validator before write
   - Check row count > 0
   - Check no null values in required fields
   - Check data quality metrics (e.g., all population > 0)
3. Implement error handling:
   - Catch duplicate key errors
   - Handle schema mismatch
   - Log errors with context
   - Support rollback if needed
4. Write tests:
   - Mock Spark DataFrame and SparkSession
   - Test successful write
   - Test schema validation errors
   - Test error logging

**Deliverables**:

- ✅ `src/data/delivery/spark_writer.py` with write logic
- ✅ Schema validation before write
- ✅ Tests with mocked Spark
- ✅ Write metrics logged

**Dependencies**:

- PySpark package
- Database schemas and validators (Task 1.4)
- Logging (Task 1.1)

**Success Criteria**:

- Data is written to Databricks successfully
- Schema is validated before write
- Write metrics are logged
- Errors are handled gracefully

---

## Cross-Agent Dependencies

**Blocks**:

- Blocks: Python Notebook Agent (need collectors/transformers/delivery modules ready)
- Blocks: QA Agent (need code ready for testing)
- Blocks: CI/CD Specialist (need Docker image for deployment)

**Depends On**:

- CI/CD Agent (logging configuration to Azure Log Analytics)
- User (exact API endpoints and Databricks connection details)

---

## Success Criteria for Milestone 3

✅ Structured logging working across all modules  
✅ Pydantic models validate all data  
✅ API clients handle retries and rate limiting  
✅ Databricks/Spark schemas defined and validated  
✅ Collectors fetch data from REST Countries and World Bank  
✅ Transformers process data with PySpark  
✅ Delivery writes validated data to Databricks  
✅ All code type-checked with typy  
✅ All code linted with ruff  
✅ Tests have > 80% coverage with mocks

---

## Risks & Mitigations

| Risk                                  | Mitigation                                             |
| ------------------------------------- | ------------------------------------------------------ |
| API rate limiting impacts development | Use mock responses in tests; implement backoff logic   |
| Spark DataFrame operations fail       | Test locally with sample data; validate schema early   |
| Data quality issues in APIs           | Add comprehensive validation; log data quality metrics |
| Type safety not enforced              | Use typy with strict mode; add tests for type errors   |
| Missing error handling                | Document error cases; add logging for all failures     |

---

## Handoff Checklist

- [ ] Logging framework configured and applied everywhere
- [ ] Pydantic models created for all data types
- [ ] API clients working with mocked responses
- [ ] Database schemas and connection wrapper ready
- [ ] Collectors fetch data from REST Countries and World Bank
- [ ] Transformers process data with PySpark
- [ ] Delivery module writes validated data
- [ ] All tests pass with > 80% coverage
- [ ] Code type-checked with typy, linted with ruff
- [ ] Docker image built for CI/CD deployment

**When Complete**: Report back to Repository Planner with completion status and any blockers.
