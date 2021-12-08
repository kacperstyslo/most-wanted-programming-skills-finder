"""
Get scraped skills from S3 bucket and save them into postgres table.
"""
# PSL
import io
from os import getenv
from typing import List, NoReturn

# Third part
import django
import boto3
import pandas as pd
from dotenv import load_dotenv

# Own
django.setup()
from jobs.models import SkillPerJobCategoryTable


class SkillsPerJobCategoryTableUpdater:
    def __init__(self) -> NoReturn:
        load_dotenv()
        self.s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=getenv("ACCESS_KEY_ID"),
            aws_secret_access_key=getenv("SECRET_ACCESS_KEY"),
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=getenv("ACCESS_KEY_ID"),
            aws_secret_access_key=getenv("SECRET_ACCESS_KEY"),
        )
        self.skills_finder_bucket_name: str = "skills-finder-storage"
        self.parts_name_of_analyzed_skills: List[str] = []

    def __call__(self, *args, **kwargs) -> NoReturn:
        self.collect_parts_names()
        self.read_data_from_parts()

    def collect_parts_names(self) -> NoReturn:
        """
        Pyspark, after analyzing the data, saves the result in parts. This function will find names
        of those parts located in s3 bucket. This function also will saved them into list.
        """
        for part_name in self.s3_resource.Bucket(
            self.skills_finder_bucket_name
        ).objects.filter(Prefix="data/most_wanted_skills"):
            if part_name.key.endswith("csv"):
                self.parts_name_of_analyzed_skills.append(part_name.key)

    def read_data_from_parts(self) -> NoReturn:
        """
        Get jobs categories from S3 bucket and update them into "JobsCategories" table.
        """
        for part_name in self.parts_name_of_analyzed_skills:
            tech_skills_csv = self.s3_client.get_object(
                Bucket=self.skills_finder_bucket_name, Key=part_name
            )

            self.update_skill_per_job_category_table_using_data_from_parts(
                pd.read_csv(
                    io.BytesIO(tech_skills_csv["Body"].read()), header=None
                )
            )

    @staticmethod
    def update_skill_per_job_category_table_using_data_from_parts(
        skill_per_job_category_df,
    ) -> NoReturn:
        """
        :param skill_per_job_category_df: Dataframe that contains in single row job_category,
        tech skill and amount of how often this skills occurred in jobs profiles site.
        :type skill_per_job_category_df: dataframe from .csv file
        """
        for row in skill_per_job_category_df.iterrows():
            SkillPerJobCategoryTable.objects.get_or_create(
                job_category=row[1][0], skill=row[1][1], amount=row[1][2]
            )


SkillsPerJobCategoryTableUpdater()()
