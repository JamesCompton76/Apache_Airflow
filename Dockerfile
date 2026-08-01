# Start with the official Airflow image you are currently using
FROM apache/airflow:2.10.2

# Install astronomer-cosmos in the main Airflow environment
RUN pip install --no-cache-dir astronomer-cosmos

# Create a virtual environment specifically for dbt and the DuckDB adapter
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-core dbt-duckdb && deactivate
