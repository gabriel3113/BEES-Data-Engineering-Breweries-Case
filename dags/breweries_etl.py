from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from airflow.utils.email import send_email
from src.extract import fetch_breweries
from datetime import timedelta
from datetime import datetime

def get_param(context, param, default):
    return context['dag_run'].conf.get(param) if context.get('dag_run') and context['dag_run'].conf.get(param) else default


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['seu_email@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="breweries_medallion_etl",
    start_date=days_ago(1),
    default_args=default_args,  
    schedule_interval="@daily",
    catchup=False,
    tags=["bees", "brewery"],
) as dag:

    def extract_with_dates(**context):
        # Define padrão: data de execução
        ds = context['ds']
        start_date = get_param(context, "start_date", ds)
        end_date = get_param(context, "end_date", ds)
        fetch_breweries(start_date=start_date, end_date=end_date)

    extract = PythonOperator(
        task_id="extract_breweries",
        python_callable=extract_with_dates,
        provide_context=True,
    )

    bronze_to_silver = BashOperator(
        task_id="bronze_to_silver",
        bash_command=(
            "spark-submit --master local[*] /opt/airflow/src/transform.py "
            "--start_date {{ dag_run.conf['start_date'] if dag_run and dag_run.conf.get('start_date') else ds }} "
            "--end_date {{ dag_run.conf['end_date'] if dag_run and dag_run.conf.get('end_date') else ds }}"
        ),
    )

    silver_to_gold = BashOperator(
        task_id="silver_to_gold",
        bash_command=(
            "spark-submit --master local[*] /opt/airflow/src/load.py "
            "--start_date {{ dag_run.conf['start_date'] if dag_run and dag_run.conf.get('start_date') else ds }} "
            "--end_date {{ dag_run.conf['end_date'] if dag_run and dag_run.conf.get('end_date') else ds }}"
        ),
    )

    extract >> bronze_to_silver >> silver_to_gold
