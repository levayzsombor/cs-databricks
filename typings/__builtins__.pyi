from collections.abc import Callable

from databricks.sdk.runtime import *
from pyspark.sql import DataFrame
from pyspark.sql.context import SQLContext
from pyspark.sql.functions import udf as U
from pyspark.sql.session import SparkSession

udf = U
spark: SparkSession
sc = spark.sparkContext
sqlContext: SQLContext
sql: Callable[[str], DataFrame]
table: Callable[[str], DataFrame]

def getArgument(name: str, defaultValue: str | None = None) -> object: ...

def displayHTML(html: str) -> None: ...
def display(
    input: object | None = None,
    *args: object,
    **kwargs: object,
) -> None: ...
