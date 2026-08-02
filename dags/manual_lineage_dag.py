from airflow import DAG
from airflow.operators.python import ExternalPythonOperator
from datetime import datetime

# We can leave PYTHON_ENV outside because it is used by Airflow to build the task, 
# not by the isolated function itself!
PYTHON_ENV = "/opt/airflow/dbt_venv/bin/python"

# --- 1. Define Python functions ---

def create_cleansed_table():
    import duckdb
    # Define paths INSIDE the function scope
    DB_PATH = "/opt/airflow/data/manual_demo.duckdb"
    PARQUET_PATH = "/opt/airflow/data/yellow_tripdata_2024-01.parquet"
    
    with duckdb.connect(DB_PATH) as conn:
        conn.execute(f"""
            CREATE OR REPLACE TABLE silver_taxi_cleansed AS 
            
            WITH source_data AS (
                SELECT * FROM '{PARQUET_PATH}'
            ),
            
            cleansed_data AS (
                SELECT
                    CAST(VendorID AS INTEGER) AS vendor_id,
                    CAST(tpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
                    CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,
                    CAST(passenger_count AS INTEGER) AS passenger_count,
                    CAST(trip_distance AS DOUBLE) AS trip_distance,
                    CAST(fare_amount AS NUMERIC(10, 2)) AS fare_amount,
                    CAST(total_amount AS NUMERIC(10, 2)) AS total_amount,
                    CAST(payment_type AS DOUBLE) AS payment_type,
                    CAST(tip_amount AS NUMERIC(10, 2)) AS tip_amount
                FROM source_data
            )
            
            SELECT *
            FROM cleansed_data
            WHERE total_amount > 0;
        """)

def create_daily_revenue_table():
    import duckdb
    DB_PATH = "/opt/airflow/data/manual_demo.duckdb"
    
    with duckdb.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE OR REPLACE TABLE fct_daily_taxi_revenue AS
            SELECT
                vendor_id,
                CAST(pickup_datetime AS DATE) AS service_date,
                COUNT(*) AS total_trips,
                SUM(trip_distance) AS total_distance_miles,
                SUM(total_amount) AS total_revenue
            FROM silver_taxi_cleansed
            GROUP BY 1, 2;
        """)

def create_payment_metrics_table():
    import duckdb
    DB_PATH = "/opt/airflow/data/manual_demo.duckdb"
    
    with duckdb.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE OR REPLACE TABLE fct_payment_type_metrics AS
            SELECT
                payment_type,
                COUNT(*) AS total_trips,
                SUM(total_amount) AS total_revenue,
                AVG(tip_amount) AS avg_tip_amount,
                AVG(trip_distance) AS avg_trip_distance_miles
            FROM silver_taxi_cleansed
            GROUP BY 1;
        """)

def create_gold_row_counts_table():
    import duckdb
    DB_PATH = "/opt/airflow/data/manual_demo.duckdb"
    
    with duckdb.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE OR REPLACE TABLE gold_row_counts AS
            SELECT 
                'fct_daily_taxi_revenue' AS table_name, 
                COUNT(*) AS row_count 
            FROM fct_daily_taxi_revenue

            UNION ALL

            SELECT 
                'fct_payment_type_metrics' AS table_name, 
                COUNT(*) AS row_count 
            FROM fct_payment_type_metrics;
        """)

# --- 2. Define the Airflow DAG ---

with DAG(
    dag_id="manual_duckdb_pipeline",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_tasks=1, 
    tags=["demo"]
) as dag:

    # --- 3. Create the Airflow Tasks ---
    
    t1 = ExternalPythonOperator(
        task_id="create_cleansed_table",
        python=PYTHON_ENV,
        python_callable=create_cleansed_table
    )
    
    t2 = ExternalPythonOperator(
        task_id="create_daily_revenue_table",
        python=PYTHON_ENV,
        python_callable=create_daily_revenue_table
    )
    
    t3 = ExternalPythonOperator(
        task_id="create_payment_metrics_table",
        python=PYTHON_ENV,
        python_callable=create_payment_metrics_table
    )
    
    t4 = ExternalPythonOperator(
        task_id="create_gold_row_counts_table",
        python=PYTHON_ENV,
        python_callable=create_gold_row_counts_table
    )

    # --- 4. The Lineage Definition ---
    
    t1 >> [t2, t3] >> t4