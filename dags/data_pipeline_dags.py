# !/usr/bin/env python3

"""
All skill finder data pipeline dags.
"""

# PSL
from datetime import datetime

# Third part
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.contrib.operators.emr_add_steps_operator import (
    EmrAddStepsOperator,
)
from airflow.contrib.operators.emr_create_job_flow_operator import (
    EmrCreateJobFlowOperator,
)
from airflow.contrib.operators.emr_terminate_job_flow_operator import (
    EmrTerminateJobFlowOperator,
)

# Own
from config import (
    BUCKET_NAME,
    EMR_JOB_FLOW,
    PYSPARK_JOBS_SUBMIT_CONFIG,
    PYSPARK_JOBS_LOCAL_LOC,
    PYSPARK_JOBS_S3_LOC,
    TECH_SKILLS_FILE_S3_LOC,
    TECH_SKILLS_FILE_LOCAL_LOC,
)
from helpers import (
    invoke_skills_scraper_lambda_handler,
    SkillsFinderStorageOperator,
)


with DAG(
    dag_id="skills_finder_pipeline",
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:
    skills_finder_storage_operator = SkillsFinderStorageOperator(BUCKET_NAME)

    start_data_pipeline = DummyOperator(task_id="start_data_pipeline", dag=dag)

    create_skills_finder_bucket = PythonOperator(
        dag=dag,
        task_id="create_skills_finder_bucket",
        python_callable=skills_finder_storage_operator.create_bucket,
    )

    create_folders_inside_skills_finder_bucket = PythonOperator(
        dag=dag,
        task_id="create_folders_inside_skills_finder_bucket",
        python_callable=skills_finder_storage_operator.create_folders_inside_s3_bucket,
        op_kwargs={
            "folders_names": ["data/scraped_skills/", "emr/_pyspark/jobs/"],
        },
    )

    upload_tech_skills_file_to_s3 = PythonOperator(
        dag=dag,
        task_id="upload_tech_skills_file_to_s3",
        python_callable=skills_finder_storage_operator.upload_local_file_to_s3_bucket,
        op_kwargs={
            "file_name": TECH_SKILLS_FILE_LOCAL_LOC,
            "s3_save_location": TECH_SKILLS_FILE_S3_LOC,
        },
    )

    upload_pyspark_jobs_to_s3 = PythonOperator(
        dag=dag,
        task_id="upload_pyspark_jobs_to_s3",
        python_callable=skills_finder_storage_operator.upload_local_file_to_s3_bucket,
        op_kwargs={
            "file_name": PYSPARK_JOBS_LOCAL_LOC,
            "s3_save_location": PYSPARK_JOBS_S3_LOC,
        },
    )

    invoke_skills_scraper_lambda_handler = PythonOperator(
        dag=dag,
        task_id="invoke_skills_scraper_lambda_handler",
        python_callable=invoke_skills_scraper_lambda_handler,
        provide_context=True,
    )

    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id="create_emr_cluster",
        job_flow_overrides=EMR_JOB_FLOW,
        aws_conn_id="aws_default",
        emr_conn_id="emr_default",
        trigger_rule="all_done",
        dag=dag,
    )

    submit_pyspark_jobs = EmrAddStepsOperator(
        task_id="submit_pyspark_jobs",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=PYSPARK_JOBS_SUBMIT_CONFIG,
        dag=dag,
    )

    check_if_pyspark_jobs_is_completed = EmrStepSensor(
        task_id="check_if_pyspark_jobs_is_completed",
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='submit_pyspark_jobs', key='return_value')[0] }}",
        aws_conn_id="aws_default",
        dag=dag,
    )

    terminate_emr_cluster = EmrTerminateJobFlowOperator(
        task_id="terminate_emr_cluster",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        dag=dag,
    )

    end_data_pipeline = DummyOperator(task_id="end_data_pipeline", dag=dag)

(
    start_data_pipeline
    >> create_skills_finder_bucket
    >> create_folders_inside_skills_finder_bucket
    >> [
        upload_tech_skills_file_to_s3,
        upload_pyspark_jobs_to_s3,
    ]
    >> invoke_skills_scraper_lambda_handler
    >> create_emr_cluster
    >> submit_pyspark_jobs
    >> check_if_pyspark_jobs_is_completed
    >> terminate_emr_cluster
    >> end_data_pipeline
)
