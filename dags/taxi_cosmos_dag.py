import os
from datetime import datetime
from pathlib import Path

from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig, ExecutionMode

DEFAULT_DBT_ROOT_PATH = Path(__file__).parent.parent / "include" / "dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))

venv_execution_config = ExecutionConfig(
    execution_mode=ExecutionMode.LOCAL,
    dbt_executable_path="/opt/airflow/dbt_venv/bin/dbt",
)

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profiles_yml_filepath=DBT_ROOT_PATH / "taxi_demo" / "profiles.yml"
)

taxi_demo_dag = DbtDag(
    project_config=ProjectConfig(DBT_ROOT_PATH / "taxi_demo"),
    profile_config=profile_config,
    execution_config=venv_execution_config,
    operator_args={"install_deps": True},
    schedule_interval="*/10 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_tasks=1,
    dag_id="taxi_dbt_cosmos_demo",
)
