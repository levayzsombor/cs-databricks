---
description: 'Best practices for Python development in Databricks environments using PySpark, Pydantic, and type safety'
applyTo: 'src/**/*.py, src/notebooks/**'
---

# Databricks Python Best Practices

Guidelines for Python development in Databricks environments, emphasizing type safety, data validation, structured logging, and testability.

## Core Principles

- **Type Safety**: All public functions must have type hints; use `typy` for runtime enforcement
- **Data Validation**: Use Pydantic models for all data structures crossing module boundaries
- **Structured Logging**: Use loguru with timestamps and severity levels (DEBUG, INFO, WARNING, ERROR)
- **Testability**: Write code with dependency injection to enable mocking in tests
- **Performance**: Write PySpark code with lazy evaluation in mind; avoid expensive operations in driver code

## Code Structure

### Module Organization

```
src/
├── data/
│   ├── __init__.py
│   ├── collectors/          # API data collection
│   │   ├── __init__.py
│   │   ├── rest_countries.py  # Collector for REST Countries API
│   │   └── world_bank.py      # Collector for World Bank API
│   ├── transformers/        # Data transformation logic
│   │   ├── __init__.py
│   │   ├── country_transform.py
│   │   └── demographics_transform.py
│   └── delivery/            # Data delivery to Databricks/Power BI
│       ├── __init__.py
│       └── spark_writer.py
├── models/                  # Pydantic data models
│   ├── __init__.py
│   ├── country.py
│   ├── demographics.py
│   └── validation.py
├── database/                # Database layer
│   ├── __init__.py
│   ├── schemas.py           # Databricks schema definitions
│   ├── connection.py        # Spark session management
│   └── validators.py        # Database validation
├── clients/                 # External API clients
│   ├── __init__.py
│   ├── base.py              # Base HTTP client with retry logic
│   ├── rest_countries.py    # REST Countries API client
│   └── world_bank.py        # World Bank API client
├── logging_config.py        # Centralized logging setup
└── notebooks/               # Orchestration notebooks only
    └── country_stats_pipeline.ipynb
```

### Nested Functions Rule

If a function is more than 10 lines OR contains nested logic, consider extracting it to its own module:

```python
# ❌ BAD: Nested logic in function
def process_country_data(raw_data):
    # 20 lines of transformation
    # 10 lines of validation
    # 15 lines of enrichment
    pass

# ✅ GOOD: Split into separate functions/modules
def process_country_data(raw_data):
    validated = validate_country_data(raw_data)
    transformed = transform_country_data(validated)
    enriched = enrich_with_demographics(transformed)
    return enriched

# Even better: move to src/data/transformers/country_transform.py
from src.data.transformers import CountryTransformer
```

## Type Hints & Type Safety

### Enforce Type Hints Everywhere

```python
# ❌ BAD: No type hints
def fetch_countries():
    return requests.get("...").json()

def process_data(records):
    return [transform(r) for r in records]

# ✅ GOOD: Full type coverage
from typing import List
from pydantic import BaseModel
from src.models import Country

def fetch_countries() -> List[dict]:
    """Fetch raw country data from REST Countries API."""
    response = requests.get("https://restcountries.com/v3.1/all")
    response.raise_for_status()
    return response.json()

def process_data(records: List[dict]) -> List[Country]:
    """Transform raw records into Country models with validation."""
    return [Country(**record) for record in records]
```

### Use Pydantic for Data Models

```python
# src/models/country.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class Country(BaseModel):
    """Validated country data model."""

    code: str = Field(..., min_length=2, max_length=3, description="ISO 3166-1 alpha-3 code")
    name: str = Field(..., min_length=1, max_length=255)
    population: int = Field(..., ge=0, description="Country population count")
    area: Optional[float] = Field(None, ge=0, description="Area in km²")
    capital: Optional[str] = None
    region: Optional[str] = None
    timezones: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('code')
    def code_must_be_uppercase(cls, v):
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "code": "USA",
                "name": "United States",
                "population": 331000000,
                "area": 9833000,
                "capital": "Washington, D.C.",
                "region": "North America"
            }
        }
```

### Type Hints for PySpark Code

```python
from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import col, row_number
from typing import Dict, Any

def process_spark_data(
    spark: SparkSession,
    input_table: str,
    filters: Dict[str, Any]
) -> DataFrame:
    """
    Process Spark DataFrame with type hints.

    Args:
        spark: SparkSession instance
        input_table: Name of input table
        filters: Dictionary of column filters

    Returns:
        Processed DataFrame
    """
    df = spark.table(input_table)

    # Apply filters
    for column, value in filters.items():
        df = df.filter(col(column) == value)

    # Transform with proper typing
    window_spec = Window.partitionBy("region").orderBy("population")
    result = df.withColumn("rank", row_number().over(window_spec))

    return result
```

## Structured Logging with Loguru

### Setup Centralized Logging

```python
# src/logging_config.py
import sys
from loguru import logger
from datetime import datetime

def setup_logging(level: str = "INFO", context_name: str = "databricks"):
    """Configure structured logging for all modules."""

    # Remove default handler
    logger.remove()

    # Console output for development
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )

    # File output for production
    logger.add(
        f"logs/{context_name}_{datetime.now().strftime('%Y%m%d')}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="INFO",  # Only INFO+ in files, DEBUG stays console-only
        rotation="500 MB"
    )

    return logger

# Import in modules
from src.logging_config import setup_logging
logger = setup_logging()
```

### Use Logging Throughout Code

```python
from loguru import logger
from src.models import Country
from typing import List

def validate_and_enrich_countries(raw_data: List[dict]) -> List[Country]:
    """Validate and enrich country data with logging."""

    logger.info(f"Starting validation of {len(raw_data)} countries")

    validated = []
    errors = []

    for idx, record in enumerate(raw_data):
        try:
            country = Country(**record)
            validated.append(country)
            logger.debug(f"Validated country: {country.code}")
        except ValueError as e:
            error_msg = f"Validation failed for record {idx}: {str(e)}"
            logger.warning(error_msg)
            errors.append({"index": idx, "error": error_msg})

    logger.info(f"Validation complete: {len(validated)} valid, {len(errors)} invalid")

    if errors:
        logger.warning(f"Validation errors: {errors}")

    return validated
```

## Testing Patterns

### Unit Test Structure

```python
# tests/test_country_model.py
import pytest
from pydantic import ValidationError
from src.models import Country

class TestCountryModel:
    """Test Country data model validation."""

    def test_valid_country_creation(self):
        """Should create valid country with all fields."""
        country = Country(
            code="USA",
            name="United States",
            population=331000000
        )
        assert country.code == "USA"
        assert country.name == "United States"

    def test_code_validation(self):
        """Should validate country code format."""
        with pytest.raises(ValidationError):
            Country(code="", name="Test", population=1000)

    def test_population_non_negative(self):
        """Should reject negative population."""
        with pytest.raises(ValidationError):
            Country(code="TST", name="Test", population=-100)

    def test_code_uppercase_conversion(self):
        """Should convert code to uppercase."""
        country = Country(code="usa", name="United States", population=331000000)
        assert country.code == "USA"
```

### Mocking API Clients

```python
# tests/test_rest_countries_collector.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.data.collectors.rest_countries import RestCountriesCollector

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    return Mock()

@pytest.fixture
def collector(mock_http_client):
    """Collector with mocked dependencies."""
    return RestCountriesCollector(http_client=mock_http_client)

def test_fetch_countries_success(collector, mock_http_client):
    """Should fetch and parse countries successfully."""
    mock_http_client.get.return_value = {
        "status": 200,
        "data": [{"code": "USA", "name": "United States"}]
    }

    result = collector.fetch_all()

    assert len(result) > 0
    mock_http_client.get.assert_called_once()

def test_fetch_countries_api_error(collector, mock_http_client):
    """Should handle API errors gracefully."""
    mock_http_client.get.side_effect = Exception("API Error")

    with pytest.raises(Exception):
        collector.fetch_all()
```

### Mocking Spark Operations

```python
# tests/test_country_transform.py
import pytest
from unittest.mock import Mock, MagicMock
from pyspark.sql import SparkSession, DataFrame
from src.data.transformers.country_transform import CountryTransformer

@pytest.fixture
def mock_spark():
    """Mock Spark session."""
    spark = MagicMock(spec=SparkSession)
    return spark

@pytest.fixture
def mock_dataframe():
    """Mock Spark DataFrame."""
    df = MagicMock(spec=DataFrame)
    df.filter.return_value = df
    df.withColumn.return_value = df
    return df

def test_transform_countries(mock_spark, mock_dataframe):
    """Should transform countries without executing actual Spark code."""
    mock_spark.table.return_value = mock_dataframe
    transformer = CountryTransformer(spark=mock_spark)

    result = transformer.process("countries_raw")

    mock_spark.table.assert_called_once_with("countries_raw")
    assert result is not None
```

## Dependency Injection for Testability

```python
# ❌ BAD: Hard dependency on external service
class CountryCollector:
    def fetch_countries(self):
        response = requests.get("https://restcountries.com/v3.1/all")
        return response.json()

# ✅ GOOD: Injected dependency, testable
from typing import Protocol

class HTTPClient(Protocol):
    """HTTP client interface."""
    def get(self, url: str) -> dict:
        ...

class CountryCollector:
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    def fetch_countries(self) -> List[dict]:
        return self.http_client.get("https://restcountries.com/v3.1/all")

# In tests: pass Mock(spec=HTTPClient)
# In production: pass RealHTTPClient()
```

## Error Handling

```python
from loguru import logger
from typing import Optional

def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    timeout_seconds: int = 10
) -> Optional[dict]:
    """Fetch with retry logic and detailed logging."""

    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=timeout_seconds)
            response.raise_for_status()
            logger.info(f"Successfully fetched {url}")
            return response.json()

        except requests.Timeout:
            logger.warning(f"Timeout fetching {url} on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts: Timeout")
                raise

        except requests.RequestException as e:
            logger.error(f"Request error fetching {url}: {str(e)}")
            if attempt == max_retries - 1:
                raise
```

## Notebook Best Practices

### Notebooks Should Be Orchestration-Only

```python
# ❌ BAD: 100 lines of transformation logic in notebook
# src/notebooks/process_data.ipynb
# [Cell 1] Complex transformations
# [Cell 2] More logic
# [Cell 3] Data validation

# ✅ GOOD: Notebook orchestrates, logic in modules
# src/notebooks/country_stats_pipeline.ipynb

# [Cell 1] Setup
from src.logging_config import setup_logging
from src.data.collectors.rest_countries import RestCountriesCollector
from src.data.transformers.country_transform import CountryTransformer
from src.data.delivery.spark_writer import SparkWriter

logger = setup_logging()

# [Cell 2] Execute pipeline
collector = RestCountriesCollector(http_client=production_client)
raw_data = collector.fetch_all()

transformer = CountryTransformer(spark=spark)
transformed_df = transformer.process_raw_data(raw_data)

writer = SparkWriter(spark=spark)
writer.write_to_table(
    df=transformed_df,
    table_name="country_stats",
    mode="overwrite"
)

logger.info("Pipeline completed successfully")
```

## API Client Patterns

### Base HTTP Client with Retry

```python
# src/clients/base.py
import requests
from typing import Dict, Any, Optional
from loguru import logger
import time

class HTTPClient:
    """Base HTTP client with retry and error handling."""

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    def get(self, url: str, params: Optional[Dict] = None) -> dict:
        """GET request with retry logic."""

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"GET {url} with params {params}")
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed after {self.max_retries} attempts")
                    raise
```

### Specific API Clients

```python
# src/clients/rest_countries.py
from src.clients.base import HTTPClient
from typing import List
from loguru import logger

class RestCountriesClient(HTTPClient):
    """REST Countries API client."""

    BASE_URL = "https://restcountries.com/v3.1"

    def get_all_countries(self) -> List[dict]:
        """Fetch all countries."""
        logger.info("Fetching all countries from REST Countries API")
        return self.get(f"{self.BASE_URL}/all")

    def get_country_by_code(self, code: str) -> dict:
        """Fetch single country by code."""
        logger.info(f"Fetching country: {code}")
        return self.get(f"{self.BASE_URL}/alpha/{code}")
```

## Performance Considerations for PySpark

```python
# ❌ BAD: Expensive operations in driver
def process_countries(spark):
    df = spark.table("countries")

    # This collects ALL data to driver — very expensive!
    for row in df.collect():
        process_row(row)

# ✅ GOOD: Keep data distributed
def process_countries(spark):
    df = spark.table("countries")

    # Operations stay distributed
    processed = df.filter(col("population") > 1000000) \
        .select("name", "population", "region") \
        .persist()  # Cache if reused

    logger.info(f"Processed {processed.count()} countries")
    return processed
```

---

## Summary Checklist

- [ ] All functions have type hints (parameters and return types)
- [ ] Pydantic models used for cross-module data
- [ ] Loguru logging with timestamps and severity
- [ ] Dependency injection for testability
- [ ] Unit tests with 100% mocks for external dependencies
- [ ] Nested logic extracted to separate modules
- [ ] Error handling with proper logging
- [ ] PySpark operations keep data distributed (no collect() to driver)
- [ ] Notebooks are orchestration-only, logic in modules
- [ ] API clients implement retry logic with backoff
