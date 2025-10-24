# import parquet

# import pyarrow
import pandas as pd



"""
Documentation:
    1. https://www.datacamp.com/tutorial/apache-parquet

    OLTP: Online Transaction Processing - PostgreSQL, MySQL, Oracle, etc. (Row-oriented databases)
    OLAP: Online Analytical Processing - Redshift, BigQuery, Snowflake, etc. (Column-oriented databases)
    Parquet is a columnar storage file format that is optimized for use with big data processing
    frameworks like Apache Spark and Apache Hive. It is designed to be efficient for both reading and
    writing large datasets, and it supports advanced features like schema evolution and compression.

    Compression Techniques:
        1. Snappy: Fast compression and decompression, suitable for real-time processing.
        2. Gzip: Higher compression ratio, but slower than Snappy.
    
    SQL Tools: Presto/Trino, DuckDB (In Memory SQL Engine), Apache Drill, Apache Impala, Apache Hive, Apache Spark

    create table employees (
        id int,
        name string,
        age int,
        department string,
        salary float
    ) location 's3://my-bucket/employees/parquet/'
"""

import pandas as pd

# Sample DataFrame
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "Los Angeles", "Chicago"]
}
df = pd.DataFrame(data)

# Write to Parquet file
df.to_parquet("data.parquet", engine="pyarrow", index=False)

print("Parquet file written successfully!")

# Read from Parquet file
df_read = pd.read_parquet("data.parquet", engine="pyarrow")
print("Data read from Parquet file:")
print(df_read)