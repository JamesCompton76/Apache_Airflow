# Apache Airflow Local Development Environment

This repository contains a local development and testing environment for Apache Airflow, powered by Docker Compose. It includes a custom `Dockerfile` configured to run dbt and DuckDB alongside Airflow using Astronomer Cosmos.

## Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* Git

## Directory Structure

Airflow requires specific folders to be mounted for the containers to run properly. Here is what goes in each:

* **`dags/`**: Your workflow definitions belong here. Drop your Python DAG files into this directory, and the scheduler will automatically parse and execute them.
* **`plugins/`**: If you write custom hooks, operators, or sensors to extend Airflow's functionality, place those Python files in this folder.
* **`config/`**: This directory is used for custom environment configurations or `airflow.cfg` overrides.
* **`logs/`**: Airflow will write all task execution history and webserver logs here. To prevent cluttering your repository, this directory is typically ignored by version control.

## Custom Docker Image

This setup uses a custom `Dockerfile` rather than the standard Airflow image to prevent dependency conflicts between Airflow and dbt. It installs:
* `astronomer-cosmos` in the main Airflow environment for dbt orchestration.
* `dbt-core` and `dbt-duckdb` inside a dedicated virtual environment (`dbt_venv`).

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

3. **Initialize the Airflow database:**
   Because we are using a custom image, you must build it before initializing the database:
   ```bash
   docker compose build
   docker compose up airflow-init
   ```

4. **Start the environment:**
   ```bash
   docker compose up -d
   ```
   *(Note: If you make further changes to the `Dockerfile`, run `docker compose up -d --build` to apply them).*

## Usage

* **Access the UI:** Navigate to `http://localhost:8080`
* **Credentials:** `airflow` / `airflow`
* **Adding Workflows:** Drop your Python DAG files into the `dags/` directory. The scheduler will automatically parse them.

## Teardown

To stop the containers while preserving your database and task history:
```bash
docker compose down
```

To completely wipe the environment clean (including the database volumes):
```bash
docker compose down -v
```
