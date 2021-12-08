"""
Airflow helpers for dags.
"""

# PSL
from json import dumps
from typing import List, NoReturn

# Third part
from boto3 import client
from airflow.hooks.S3_hook import S3Hook
from airflow.contrib.hooks.aws_lambda_hook import AwsLambdaHook


class SkillsFinderStorageOperator:
    """
    This class store methods whats prepare storage for skills finder app.
    """

    def __init__(self, bucket_name: str) -> NoReturn:
        self.bucket_name: str = bucket_name
        self.region_name: str = "us-east-1"
        self.s3_hook = S3Hook()
        self.s3_client = client("s3")

    def create_bucket(self) -> NoReturn:
        """
        In this created bucket skills finder app will store all data.
        """
        self.s3_hook.create_bucket(
            bucket_name=self.bucket_name, region_name=self.region_name
        )

    def create_folders_inside_s3_bucket(
        self, folders_names: List[str]
    ) -> NoReturn:
        """
        Created to organize data in skills finder bucket located on s3.
        :param folders_names: Names and folders location in s3 bucket
        :type folders_names: str
        """
        for folder_name in folders_names:
            self.s3_client.put_object(
                Bucket=self.bucket_name, Body="", Key=folder_name
            )

    def upload_local_file_to_s3_bucket(
        self, file_name: str, s3_save_location: str
    ) -> NoReturn:
        """
        Uploading tech_skills.txt (data set of technical skills) & pyspark_jobs to s3 bucket.
        :param file_name: file name and location on local drive
        :type file_name: str
        :param str s3_save_location: where local file will be stored in s3 bucket
        :type s3_save_location: str
        """
        self.s3_hook.load_file(
            bucket_name=self.bucket_name,
            filename=file_name,
            key=s3_save_location,
            replace=True,
        )


def invoke_skills_scraper_lambda_handler(ds, **kwargs) -> NoReturn:
    """
    Invoke skills scraper by using lambda handler. Skills scraper already have prepared runtime env
    by terraform.
    :param ds: execution date as YYYY-MM-DD
    :type ds: str
    :param **kwargs: airflow inject key-word arguments into this fnc
    """
    lambda_hook = AwsLambdaHook(
        "skills_scraper",
        region_name="us-east-1",
        log_type="None",
        qualifier="$LATEST",
        invocation_type="RequestResponse",
        config=None,
        aws_conn_id="aws_default",
    )
    lambda_hook.invoke_lambda(payload=dumps({}))
