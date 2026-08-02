from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import time

# --- 1. Define dummy Python functions ---

def create_table1():
    print("Mocking creation of Table 1")
    time.sleep(2) # Pausing for 2 seconds so you can watch the tasks transition in the UI

def create_table2():
    print("Mocking creation of Table 2")
    time.sleep(2)

def create_table3():
    print("Mocking creation of Table 3")
    time.sleep(2)

def create_table4():
    print("Mocking creation of Table 4")
    time.sleep(2)

# --- 2. Define the Airflow DAG ---

with DAG(
    dag_id="manual_mock_lineage_demo",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["demo"]
) as dag:

    # --- 3. Create the Airflow Tasks ---
    
    t1 = PythonOperator(task_id="create_table1", python_callable=create_table1)
    t2 = PythonOperator(task_id="create_table2", python_callable=create_table2)
    t3 = PythonOperator(task_id="create_table3", python_callable=create_table3)
    t4 = PythonOperator(task_id="create_table4", python_callable=create_table4)

    # --- 4. The Lineage Definition ---
    
    t1 >> [t2, t3] >> t4
