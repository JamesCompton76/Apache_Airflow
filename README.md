# Apache Airflow Local Development Environment

This repository contains a local development and testing environment for Apache Airflow, powered by Docker Compose.

## Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* Git

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
   Run the database migrations and create the default admin user:
   ```bash
   docker compose up airflow-init
   ```

4. **Start the environment:**
   ```bash
   docker compose up -d
   ```

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
