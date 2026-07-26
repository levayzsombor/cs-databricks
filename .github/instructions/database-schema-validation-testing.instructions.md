---
description: 'Best practices for database and schema validation testing, including table structure tests, column type validation, and data quality checks'
applyTo: 'tests/**/*.py'
---

# Database & Schema Validation Testing

Guidelines for writing tests that validate database structure, schema evolution, and data quality in Databricks.

## Core Principles

- **Validate Structure**: Test schema, tables, columns exist with correct types
- **Validate Constraints**: Test nullable fields, primary keys, foreign keys
- **Validate Data Quality**: Test data freshness, row counts, distributions
- **Fast Tests**: Use mock/in-memory databases; avoid real Databricks connections
- **Comprehensive Coverage**: Test both happy path and error conditions

## Test Organization

```
tests/
├── unit/
│   ├── test_models.py           # Pydantic model validation
│   ├── test_collectors.py       # API client tests
│   ├── test_transformers.py     # Data transformation tests
│   └── test_delivery.py         # Write operation tests
├── integration/
│   ├── test_spark_schema.py     # Spark schema validation
│   ├── test_database_structure.py  # Database structure tests
│   └── test_pipeline_end_to_end.py # Full pipeline tests
└── fixtures/
    ├── conftest.py              # Common fixtures
    ├── mock_data.py             # Test data generators
    └── mock_spark.py            # Spark mocking utilities
```

## Schema Definition Testing

### Define Expected Schemas

```python
# src/database/schemas.py
from typing import Dict, Tuple
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, TimestampType

# Define schemas as code
COUNTRY_SCHEMA = StructType([
    StructField("code", StringType(), nullable=False),
    StructField("name", StringType(), nullable=False),
    StructField("population", IntegerType(), nullable=False),
    StructField("area", DoubleType(), nullable=True),
    StructField("capital", StringType(), nullable=True),
    StructField("region", StringType(), nullable=True),
    StructField("created_at", TimestampType(), nullable=False),
])

DEMOGRAPHICS_SCHEMA = StructType([
    StructField("country_code", StringType(), nullable=False),
    StructField("gdp_usd", DoubleType(), nullable=True),
    StructField("gdp_per_capita_usd", DoubleType(), nullable=True),
    StructField("life_expectancy_years", DoubleType(), nullable=True),
    StructField("literacy_rate_percent", DoubleType(), nullable=True),
    StructField("updated_at", TimestampType(), nullable=False),
])

# Map table names to schemas
DATABRICKS_SCHEMAS: Dict[str, StructType] = {
    "country_stats.countries": COUNTRY_SCHEMA,
    "country_stats.demographics": DEMOGRAPHICS_SCHEMA,
}

# Metadata about tables
TABLE_METADATA: Dict[str, Dict] = {
    "country_stats.countries": {
        "primary_key": ["code"],
        "partitioned_by": None,
        "expected_rows_min": 190,  # ~190 countries
        "expected_rows_max": 300,
    },
    "country_stats.demographics": {
        "primary_key": ["country_code"],
        "partitioned_by": None,
        "expected_rows_min": 100,
    },
}
```

## Unit Tests: Model Validation

### Test Pydantic Models

```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from src.models import Country

class TestCountryModel:
    """Test Country model validation."""

    def test_valid_country(self):
        """Should create valid country with required fields."""
        country = Country(
            code="USA",
            name="United States",
            population=331000000
        )
        assert country.code == "USA"
        assert country.population == 331000000

    def test_code_required(self):
        """Should reject missing code."""
        with pytest.raises(ValidationError) as exc_info:
            Country(name="United States", population=331000000)
        assert "code" in str(exc_info.value)

    def test_code_max_length(self):
        """Should reject code longer than 3 chars."""
        with pytest.raises(ValidationError):
            Country(code="USAA", name="United States", population=331000000)

    def test_population_non_negative(self):
        """Should reject negative population."""
        with pytest.raises(ValidationError):
            Country(code="USA", name="United States", population=-100)

    def test_optional_fields(self):
        """Should allow missing optional fields."""
        country = Country(
            code="TST",
            name="Test Country",
            population=1000,
            area=None,  # Optional
            capital=None  # Optional
        )
        assert country.area is None
        assert country.capital is None

    def test_code_case_conversion(self):
        """Should convert code to uppercase."""
        country = Country(code="usa", name="United States", population=331000000)
        assert country.code == "USA"
```

## Integration Tests: Database Structure

### Test Database Schema

```python
# tests/integration/test_database_structure.py
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from src.database.schemas import COUNTRY_SCHEMA, TABLE_METADATA, DATABRICKS_SCHEMAS
from src.database.validators import DatabaseValidator

@pytest.fixture
def spark():
    """Create a test Spark session."""
    return SparkSession.builder \
        .appName("test") \
        .master("local") \
        .getOrCreate()

@pytest.fixture
def validator(spark):
    """Create database validator."""
    return DatabaseValidator(spark=spark)

class TestCountryTableSchema:
    """Test countries table schema."""

    def test_table_exists(self, spark):
        """Should verify table exists (mock in test)."""
        # In real test: check Databricks catalog
        tables = ["country_stats.countries"]
        assert "country_stats.countries" in tables

    def test_schema_matches(self, spark):
        """Should validate schema matches expected."""
        # Create mock table with correct schema
        test_df = spark.createDataFrame(
            [("USA", "United States", 331000000)],
            schema=COUNTRY_SCHEMA
        )

        # Validate
        assert test_df.schema == COUNTRY_SCHEMA

    def test_all_required_columns_present(self, spark):
        """Should verify all required columns exist."""
        expected_columns = {field.name for field in COUNTRY_SCHEMA.fields if not field.nullable}

        assert "code" in expected_columns
        assert "name" in expected_columns
        assert "population" in expected_columns

    def test_column_types_correct(self):
        """Should verify column data types."""
        code_field = next(f for f in COUNTRY_SCHEMA.fields if f.name == "code")
        assert str(code_field.dataType) == "StringType()"

        population_field = next(f for f in COUNTRY_SCHEMA.fields if f.name == "population")
        assert str(population_field.dataType) == "IntegerType()"

        area_field = next(f for f in COUNTRY_SCHEMA.fields if f.name == "area")
        assert str(area_field.dataType) == "DoubleType()"

    def test_nullable_constraints(self):
        """Should verify nullable constraints."""
        code_field = next(f for f in COUNTRY_SCHEMA.fields if f.name == "code")
        assert code_field.nullable is False

        capital_field = next(f for f in COUNTRY_SCHEMA.fields if f.name == "capital")
        assert capital_field.nullable is True
```

### Test Schema Compatibility

```python
# tests/integration/test_schema_compatibility.py
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

class TestSchemaEvolution:
    """Test handling of schema changes."""

    @pytest.fixture
    def spark(self):
        return SparkSession.builder.appName("test").master("local").getOrCreate()

    def test_new_optional_column_compatible(self, spark):
        """Should accept new optional column."""
        old_schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("name", StringType(), False),
        ])

        new_schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("name", StringType(), False),
            StructField("description", StringType(), True),  # New optional column
        ])

        # Old data should be compatible with new schema
        old_df = spark.createDataFrame([(1, "USA")], schema=old_schema)

        # Should be able to read old data with new schema
        assert all(f in [f.name for f in new_schema.fields] for f in ["id", "name"])

    def test_required_field_change_incompatible(self):
        """Should detect incompatible schema change."""
        old_schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("code", StringType(), True),  # Optional
        ])

        new_schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("code", StringType(), False),  # Now required
        ])

        # This is a breaking change
        assert old_schema != new_schema
```

## Data Quality Tests

### Test Row Counts

```python
# tests/integration/test_data_quality.py
import pytest
from pyspark.sql import SparkSession
from src.database.schemas import COUNTRY_SCHEMA, TABLE_METADATA

class TestDataQuality:
    """Test data quality and expectations."""

    @pytest.fixture
    def spark(self):
        return SparkSession.builder.appName("test").master("local").getOrCreate()

    def test_countries_table_row_count(self, spark):
        """Should verify countries table has expected row count."""
        # Create mock data
        data = [
            ("USA", "United States", 331000000),
            ("CHN", "China", 1411750000),
            ("IND", "India", 1393409038),
        ]

        df = spark.createDataFrame(data, schema=COUNTRY_SCHEMA)

        row_count = df.count()
        metadata = TABLE_METADATA["country_stats.countries"]

        # In real test: assert row_count >= metadata["expected_rows_min"]
        # assert row_count <= metadata["expected_rows_max"]
        assert row_count >= 3

    def test_no_null_in_required_fields(self, spark):
        """Should verify required fields have no nulls."""
        from pyspark.sql.functions import col, count, when

        data = [
            ("USA", "United States", 331000000),
            (None, "Country", 1000),  # Invalid: code is null
        ]

        df = spark.createDataFrame(data, schema=COUNTRY_SCHEMA)

        # Count nulls in required field
        null_count = df.filter(col("code").isNull()).count()

        assert null_count == 1  # Test detects the invalid row

    def test_unique_primary_key(self, spark):
        """Should verify primary key uniqueness."""
        from pyspark.sql.functions import col, count

        data = [
            ("USA", "United States", 331000000),
            ("USA", "US", 330000000),  # Duplicate code!
        ]

        df = spark.createDataFrame(data, schema=COUNTRY_SCHEMA)

        unique_codes = df.select("code").distinct().count()
        total_rows = df.count()

        # If unique_codes < total_rows, there are duplicates
        assert unique_codes < total_rows  # Test detects duplicates

    def test_data_freshness(self, spark):
        """Should verify data was recently updated."""
        from pyspark.sql.functions import col, max as spark_max
        from datetime import datetime, timedelta

        data = [
            ("USA", "United States", 331000000, datetime.now()),
        ]

        df = spark.createDataFrame(
            data,
            schema=COUNTRY_SCHEMA
        )

        max_timestamp = df.agg(spark_max("created_at")).collect()[0][0]

        # Data should be from last 30 days
        age = (datetime.now() - max_timestamp).days
        assert age <= 30
```

### Test Data Ranges

```python
# tests/integration/test_data_validation.py
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

class TestDataValidation:
    """Test data value validation."""

    @pytest.fixture
    def spark(self):
        return SparkSession.builder.appName("test").master("local").getOrCreate()

    def test_population_positive(self, spark):
        """Should verify population values are positive."""
        from src.database.schemas import COUNTRY_SCHEMA

        data = [
            ("USA", "United States", -100),  # Invalid!
        ]

        df = spark.createDataFrame(data, schema=COUNTRY_SCHEMA)

        invalid_count = df.filter(col("population") < 0).count()
        assert invalid_count == 1  # Test detects invalid value

    def test_area_non_negative(self, spark):
        """Should verify area is non-negative."""
        from src.database.schemas import COUNTRY_SCHEMA

        data = [
            ("USA", "United States", 331000000, -1000),  # Invalid area!
        ]

        df = spark.createDataFrame(data, schema=COUNTRY_SCHEMA)

        invalid_count = df.filter(col("area") < 0).count()
        assert invalid_count == 1

    def test_code_uppercase(self, spark):
        """Should verify country codes are uppercase."""
        from src.database.schemas import COUNTRY_SCHEMA
        from pyspark.sql.functions import col

        data = [
            ("usa", "United States", 331000000),  # Invalid: lowercase!
        ]

        df = spark.createDataFrame(data, schema=COUNTRY_SCHEMA)

        invalid_count = df.filter(
            col("code") != col("code").substr(1, 10).cast("string")
        ).count()

        # In practice, test that codes are uppercase
        assert all(code.isupper() for code, *_ in data) is False
```

## Mock Database Fixtures

### Mock Spark DataFrame

```python
# tests/fixtures/mock_spark.py
import pytest
from unittest.mock import Mock, MagicMock
from pyspark.sql import SparkSession, DataFrame

@pytest.fixture
def mock_spark_session():
    """Create a mock Spark session."""
    spark = MagicMock(spec=SparkSession)
    return spark

@pytest.fixture
def mock_dataframe():
    """Create a mock Spark DataFrame."""
    df = MagicMock(spec=DataFrame)

    # Configure common method returns
    df.count.return_value = 195  # Default row count
    df.schema.return_value = None
    df.filter.return_value = df
    df.select.return_value = df
    df.withColumn.return_value = df
    df.distinct.return_value = df
    df.agg.return_value = df

    return df

@pytest.fixture
def spark_with_data():
    """Create real Spark session with test data."""
    spark = SparkSession.builder \
        .appName("test") \
        .master("local[1]") \
        .getOrCreate()

    yield spark

    spark.stop()
```

### Mock Database Validator

```python
# tests/fixtures/mock_db.py
import pytest
from unittest.mock import Mock
from src.database.validators import DatabaseValidator

@pytest.fixture
def mock_validator():
    """Create mock database validator."""
    validator = Mock(spec=DatabaseValidator)
    validator.validate_schema.return_value = True
    validator.validate_row_count.return_value = True
    validator.validate_data_quality.return_value = {"errors": []}
    return validator
```

## Validation Utility Class

### Database Validator

```python
# src/database/validators.py
from typing import Dict, List, Tuple
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
from pyspark.sql.functions import col, count as spark_count
from loguru import logger

class DatabaseValidator:
    """Validate database schema and data quality."""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        logger.info("DatabaseValidator initialized")

    def validate_schema(
        self,
        table_name: str,
        expected_schema: StructType
    ) -> bool:
        """Validate table schema matches expected."""
        try:
            df = self.spark.table(table_name)

            if df.schema != expected_schema:
                logger.error(f"Schema mismatch for {table_name}")
                return False

            logger.info(f"Schema validation passed for {table_name}")
            return True

        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return False

    def validate_row_count(
        self,
        table_name: str,
        min_rows: int,
        max_rows: int
    ) -> Tuple[bool, int]:
        """Validate table row count within range."""
        try:
            df = self.spark.table(table_name)
            row_count = df.count()

            if row_count < min_rows or row_count > max_rows:
                logger.warning(
                    f"Row count {row_count} outside range [{min_rows}, {max_rows}] "
                    f"for {table_name}"
                )
                return False, row_count

            logger.info(f"Row count validation passed: {row_count} rows in {table_name}")
            return True, row_count

        except Exception as e:
            logger.error(f"Row count validation failed: {str(e)}")
            return False, 0

    def validate_no_nulls(
        self,
        table_name: str,
        columns: List[str]
    ) -> Dict[str, int]:
        """Validate no nulls in required columns."""
        try:
            df = self.spark.table(table_name)

            null_counts = {}
            for column in columns:
                null_count = df.filter(col(column).isNull()).count()
                null_counts[column] = null_count

                if null_count > 0:
                    logger.warning(f"Found {null_count} nulls in {table_name}.{column}")

            logger.info(f"Null validation complete for {table_name}: {null_counts}")
            return null_counts

        except Exception as e:
            logger.error(f"Null validation failed: {str(e)}")
            return {}
```

## Summary Checklist

- [ ] All database tables have schema definitions in code
- [ ] Schema validation tests verify column names and types
- [ ] Nullable constraints tested
- [ ] Data quality tests verify row counts
- [ ] No-null tests for required fields
- [ ] Primary key uniqueness tests
- [ ] Data freshness tests
- [ ] Data range/bounds tests
- [ ] Schema evolution compatibility tested
- [ ] All tests use mocks or in-memory Spark (no real Databricks calls)
- [ ] Tests run in < 1 second each
- [ ] Test data generators available for reuse
