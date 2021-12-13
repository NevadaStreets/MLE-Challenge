try:

    from datetime import timedelta
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    from datetime import datetime
    import pandas as pd
    from utils.data_processor import DataProcessor
    from utils.linear_model import LinearModel

    print("All modules lodaed")
except Exception as e:
    print("Error  {} ".format(e))

def processing_data(**context):
    try:
        print("Process training data")
        dp = DataProcessor()
        dp.process_traning_data()
        dp.save_data()
        context['ti'].xcom_push(key='status', value="Data processed successfully")
        print("Data processed successfully ")
    except Exception as e:
        print("Error  {} ".format(e))
        context['ti'].xcom_push(key='status', value="Error: data couldn't be processed")


def traning_model(**context):
    try:
        print("Training model")
        message = context.get("ti").xcom_pull(key="status")
        print(f"Message received from previous job : {message}")
        lm = LinearModel()
        lm.train()
        lm.save()
    except Exception as e:
        print("Error found!")
        print("Error  {} ".format(e))

with DAG(
        dag_id="ml_pipe",
        schedule_interval="@daily",
        default_args={
            "owner": "airflow",
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
            "start_date": datetime(2021, 1, 1),
        },
        catchup=False) as f:

    processing_data = PythonOperator(
        task_id="processing_data",
        python_callable=processing_data,
        provide_context=True,
    )

    traning_model = PythonOperator(
        task_id="traning_model",
        python_callable=traning_model,
        provide_context=True,
    )

processing_data >> traning_model