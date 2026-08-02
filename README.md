# Apache Airflow Local Development Environment[cite: 2]

This repository contains a local development and testing environment for Apache Airflow, powered by Docker Compose.[cite: 2] It includes a custom `Dockerfile` configured to run dbt and DuckDB alongside Airflow using Astronomer Cosmos.[cite: 2]

## Prerequisites[cite: 2]

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)[cite: 2]
* Git[cite: 2]

## Directory Structure[cite: 2]

Airflow requires specific folders to be mounted for the containers to run properly.[cite: 2] Here is what goes in each:[cite: 2]

* **`dags/`**: Your workflow definitions belong here.[cite: 2] Drop your Python DAG files into this directory, and the scheduler will automatically parse and execute them.[cite: 2]
* **`include/`**: Put your dbt projects in this directory (e.g., `include/dbt/taxi_demo`).[cite: 2] Astronomer Cosmos best practices dictate keeping dbt files separate from `dags/` to keep the Airflow scheduler running efficiently.[cite: 2]
* **`data/`**: Used for local data storage, such as raw Parquet files and your DuckDB database file.[cite: 2] **Note:** You must map `- ${AIRFLOW_PROJ_DIR:-.}/data:/opt/airflow/data` under volumes in your `docker-compose.yaml` for Airflow to access it.[cite: 2]
* **`plugins/`**: If you write custom hooks, operators, or sensors to extend Airflow's functionality, place those Python files in this folder.[cite: 2]
* **`config/`**: This directory is used for custom environment configurations or `airflow.cfg` overrides.[cite: 2]
* **`logs/`**: Airflow will write all task execution history and webserver logs here.[cite: 2] To prevent cluttering your repository, this directory is typically ignored by version control.[cite: 2]

## Custom Docker Image[cite: 2]

This setup uses a custom `Dockerfile` rather than the standard Airflow image to prevent dependency conflicts between Airflow and dbt.[cite: 2] It installs:[cite: 2]
* `astronomer-cosmos` in the main Airflow environment for dbt orchestration.[cite: 2]
* `dbt-core` and `dbt-duckdb` inside a dedicated virtual environment (`dbt_venv`).[cite: 2]

## System Architecture & Cosmos Configuration[cite: 2]

This project integrates Apache Airflow with dbt using Astronomer Cosmos.[cite: 2] To ensure stable execution against a local DuckDB database, the following configurations are required:[cite: 2]

### 1. Docker Volume Mappings[cite: 2]
The default Airflow `docker-compose.yaml` does not map custom directories.[cite: 2] Ensure the `include/` directory is mapped in the `volumes` section so the scheduler can parse the `dbt_project.yml` and `profiles.yml` files:[cite: 2]
```yaml
volumes:
  - ${AIRFLOW_PROJ_DIR:-.}/include:/opt/airflow/include
```

### 2. Astronomer Cosmos Execution Mode[cite: 2]
Do not use `ExecutionMode.VIRTUALENV`.[cite: 2] This causes Cosmos to attempt building an empty Python environment in the `/tmp` directory on every run, which will fail to find `dbt-duckdb`.[cite: 2] 
Instead, use `ExecutionMode.LOCAL` and point it directly to the pre-built virtual environment configured in the Dockerfile:[cite: 2]
```python
ExecutionConfig(
    execution_mode=ExecutionMode.LOCAL,
    dbt_executable_path="/opt/airflow/dbt_venv/bin/dbt",
)
```

### 3. DuckDB Concurrency Limits[cite: 2]
DuckDB is an in-process database and strictly requires a single writer.[cite: 2] Because Cosmos automatically parallelizes dbt models that share dependencies, it will cause `IO Error: Could not set lock on file` crashes if two models execute simultaneously.[cite: 2] 
To prevent this, the DAG is throttled to sequential execution using:[cite: 2]
```python
max_active_tasks=1
```

## DAG Lineage Models

This project supports both automated dbt lineage and traditional manual Airflow lineage.

### 1. Automated Lineage (Astronomer Cosmos)
When you place a dbt project in the `include/` directory, Cosmos automatically parses the `{{ ref() }}` statements in your `.sql` files and translates them into a 1-to-1 Airflow dependency graph. You do not need to manually define the execution order in Python.

### 2. Manual Lineage (Traditional Airflow)
To build a traditional DAG without dbt, you can define tasks and their dependencies manually using the `>>` bitshift operator. Drop a standard Python DAG into the `dags/` folder:

```python
t1 >> [t2, t3] >> t4
```
*Note: The main Airflow environment does not have the `duckdb` Python library installed by default (it is isolated in `dbt_venv`). For testing manual lineage graphs without database connections, use dummy functions like `time.sleep()`.*

## Initial Setup[cite: 2]

1. **Clone the repository:**[cite: 2]
   ```bash
   git clone [https://github.com/JamesCompton76/apache-airflow-docker.git](https://github.com/JamesCompton76/apache-airflow-docker.git)
   cd apache-airflow-docker
   ```

2. **Set up host user permissions:**[cite: 2]
   To ensure Airflow doesn't create root-owned files in your `dags/` and `logs/` directories, create a `.env` file with your user ID:[cite: 2]
   ```bash
   echo -e "AIRFLOW_UID=$(id -u)" > .env
   ```

3. **Optional: Download Sample Data:**[cite: 2]
   If you want to test the dbt pipeline with the NYC Yellow Taxi dataset, you can automatically download the January 2024 Parquet file directly into your `data/` directory:[cite: 2]
   ```bash
   curl -o data/yellow_tripdata_2024-01.parquet [https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet)
   ```

4. **Initialize the Airflow database:**[cite: 2]
   Because we are using a custom image, you must build it before initializing the database:[cite: 2]
   ```bash
   docker compose build
   docker compose up airflow-init
   ```

5. **Start the environment:**[cite: 2]
   ```bash
   docker compose up -d
   ```
   *(Note: If you make further changes to the `Dockerfile`, run `docker compose up -d --build` to apply them).*[cite: 2]

## Usage[cite: 2]

* **Access the UI:** Navigate to `http://localhost:8080`[cite: 2]
* **Credentials:** `airflow` / `airflow`[cite: 2]
* **Adding Workflows:** Drop your Python DAG files into the `dags/` directory.[cite: 2] The scheduler will automatically parse them.[cite: 2]

## Teardown[cite: 2]

To stop the containers while preserving your database and task history:[cite: 2]
```bash
docker compose down
```

To completely wipe the environment clean (including the database volumes):[cite: 2]
```bash
docker compose down -v
```
