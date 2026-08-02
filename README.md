# Apache Airflow Local Development Environment

This repository contains a local development and testing environment for Apache Airflow, powered by Docker Compose. It includes a custom `Dockerfile` configured to run dbt and DuckDB alongside Airflow using Astronomer Cosmos.

## Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* Git

## Directory Structure

Airflow requires specific folders to be mounted for the containers to run properly. Here is what goes in each:

* **`dags/`**: Your workflow definitions belong here. Drop your Python DAG files into this directory, and the scheduler will automatically parse and execute them.
* **`include/`**: Put your dbt projects in this directory (e.g., `include/dbt/taxi_demo`). Astronomer Cosmos best practices dictate keeping dbt files separate from `dags/` to keep the Airflow scheduler running efficiently.
* **`data/`**: Used for local data storage, such as raw Parquet files and your DuckDB database file. **Note:** You must map `- ${AIRFLOW_PROJ_DIR:-.}/data:/opt/airflow/data` under volumes in your `docker-compose.yaml` for Airflow to access it.
* **`plugins/`**: If you write custom hooks, operators, or sensors to extend Airflow's functionality, place those Python files in this folder.
* **`config/`**: This directory is used for custom environment configurations or `airflow.cfg` overrides.
* **`logs/`**: Airflow will write all task execution history and webserver logs here. To prevent cluttering your repository, this directory is typically ignored by version control.

## Custom Docker Image

This setup uses a custom `Dockerfile` rather than the standard Airflow image to prevent dependency conflicts between Airflow and dbt. It installs:
* `astronomer-cosmos` in the main Airflow environment for dbt orchestration.
* `dbt-core` and `dbt-duckdb` inside a dedicated virtual environment (`dbt_venv`).

## System Architecture & Cosmos Configuration

This project integrates Apache Airflow with dbt using Astronomer Cosmos. To ensure stable execution against a local DuckDB database, the following configurations are required:

### 1. Docker Volume Mappings
The default Airflow `docker-compose.yaml` does not map custom directories. Ensure the `include/` directory is mapped in the `volumes` section so the scheduler can parse the `dbt_project.yml` and `profiles.yml` files:
```yaml
volumes:
  - ${AIRFLOW_PROJ_DIR:-.}/include:/opt/airflow/include
```

### 2. Astronomer Cosmos Execution Mode
Do not use `ExecutionMode.VIRTUALENV`. This causes Cosmos to attempt building an empty Python environment in the `/tmp` directory on every run, which will fail to find `dbt-duckdb`. 
Instead, use `ExecutionMode.LOCAL` and point it directly to the pre-built virtual environment configured in the Dockerfile:
```python
ExecutionConfig(
    execution_mode=ExecutionMode.LOCAL,
    dbt_executable_path="/opt/airflow/dbt_venv/bin/dbt",
)
```

### 3. DuckDB Concurrency Limits
DuckDB is an in-process database and strictly requires a single writer. Because Cosmos automatically parallelizes dbt models that share dependencies, it will cause `IO Error: Could not set lock on file` crashes if two models execute simultaneously. 
To prevent this, the DAG is throttled to sequential execution using:
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

## Initial Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/JamesCompton76/apache-airflow-docker.git](https://github.com/JamesCompton76/apache-airflow-docker.git)
   cd apache-airflow-docker
   ```

2. **Set up host user permissions:**
   To ensure Airflow doesn't create root-owned files in your `dags/` and `logs/` directories, create a `.env` file with your user ID:
   ```bash
   echo -e "AIRFLOW_UID=$(id -u)" > .env
   ```

3. **Optional: Download Sample Data:**
   If you want to test the dbt pipeline with the NYC Yellow Taxi dataset, you can automatically download the January 2024 Parquet file directly into your `data/` directory:
   ```bash
   curl -o data/yellow_tripdata_2024-01.parquet [https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet)
   ```

4. **Initialize the Airflow database:**
   Because we are using a custom image, you must build it before initializing the database:
   ```bash
   docker compose build
   docker compose up airflow-init
   ```

5. **Start the environment:**
   ```bash
   docker compose up -d
   ```
   *(Note: If you make further changes to the `Dockerfile`, run `docker compose up -d --build` to apply them).*

## Usage

* **Access the UI:** Navigate to `http://localhost:8080`
* **Credentials:** `airflow` / `airflow`
* **Adding Workflows:** Drop your Python DAG files into the `dags/` directory. The scheduler will automatically parse them.
* **Scheduling DAGs:** To change how often a DAG runs, modify the `schedule_interval` parameter within your Python file (e.g., `schedule_interval="*/10 * * * *"`). Airflow accepts standard cron expressions, presets like `@daily`, or `None` for purely manual triggers. If you need help writing or translating cron syntax, [Crontab.guru](https://crontab.guru/) is an excellent interactive editor.

## Teardown

To stop the containers while preserving your database and task history:
```bash
docker compose down
```

To completely wipe the environment clean (including the database volumes):
```bash
docker compose down -v
```
