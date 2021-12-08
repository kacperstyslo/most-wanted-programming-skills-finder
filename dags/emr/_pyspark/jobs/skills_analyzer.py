# !/usr/bin/env python3

"""
Those "pyspark jobs" analyze tech skills scraped from jobs profiles. After analyze, one of this
"pyspark job" will save results into S3 bucket.
"""

# PSL
from re import findall
from typing import List, Tuple, NoReturn

# Third part
from pyspark.rdd import RDD
from pyspark import SparkContext
from pyspark.sql.functions import desc
from pyspark.sql.dataframe import DataFrame
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession, SQLContext


def create_pyspark_operators() -> Tuple[
    SparkSession, SparkContext, StreamingContext, SQLContext
]:
    """
    This functions creates and returns two pyspark operators.
    :returns: SparkSession, SparkContext, StreamingContext, SQLContext, SparkSession
    """
    spark_session = SparkSession.builder.appName(
        "skills-analyzer"
    ).getOrCreate()
    spark_context = spark_session.sparkContext
    streaming_context = StreamingContext(spark_context, 1)
    sql_context = SQLContext(spark_context)
    return spark_session, spark_context, streaming_context, sql_context


def __load_csv_from_bucket_into_rdd(sql_context_) -> RDD:
    """
    This method load skills.csv that contains all scraped skills and job profiles.
    :param sql_context_:
    :return: RDD that contains scraped skills and jobs profiles
    :rtype: RDD
    """
    return (
        sql_context_.read.options(header=True, delimiter=",")
        .csv("s3://skills-finder-storage/data/scraped_skills/skills.csv")
        .rdd.map(list)
    )


def __remove_punctuation_from_rdd(
    skills_and_jobs_categories_: List[str],
) -> RDD:
    """
    :param skills_and_jobs_categories_: skills and jobs categories
    :type skills_and_jobs_categories_: List[str]
    :return: RDD contains skills name & job profile, skills names are uppercase
    (easier to group by later)
    :rtype: RDD
    """
    skills_uppercase: List[str] = [
        skill.upper()
        for skill in findall(r"[\w']+", skills_and_jobs_categories_[0])
    ]
    return [skills_uppercase, skills_and_jobs_categories_[-1]]


def __load_tech_skills_collection(spark_session_) -> List[str]:
    """
    This method will load all words that will be omitted in the analysis named:
    -> (remove_whitespaces_and_no_tech_from_rdd)
    :param spark_session_:
    :rtype: List[str]
    """
    tech_skills: List[str] = spark_session_.read.text(
        "s3://skills-finder-storage/data/tech_skills.txt"
    ).collect()
    return [str(row["value"].upper()) for row in tech_skills]


def __remove_whitespaces_and_no_tech_words_from_rdd(
    skills_and_jobs_categories_: RDD, spark_session_
) -> RDD:
    """
    Removing whitespaces and no tech words from skills.
    :param skills_and_jobs_categories_: one record -> skill(tech & no tech skill) & job category
    :type skills_and_jobs_categories_: RDD
    :param spark_session_:
    :return: Clear RDD that contains only tech skills and job categories
    :rtype: RDD
    """
    tech_skills: List[str] = __load_tech_skills_collection(spark_session_)
    return (
        skills_and_jobs_categories_.map(
            lambda skills_jobs_: [
                [element, skills_jobs_[1]] for element in skills_jobs_[0]
            ]
        )
        .flatMap(lambda skills_jobs_: skills_jobs_)
        .filter(
            lambda skills_jobs_: skills_jobs_[0] != ""
            and skills_jobs_[0] in tech_skills
            and not skills_jobs_[0].isdigit()
        )
    )


def __transform_cleaned_rdd_into_df(
    cleaned_skills_and_jobs_categories_: RDD, sql_context_
) -> DataFrame:
    """
    :param cleaned_skills_and_jobs_categories_: only tech skills & job categories without
    whitespaces & punctuation
    :type cleaned_skills_and_jobs_categories_: RDD
    :param sql_context_:
    :return: Dataframe contains in one column scraped skill, in second one job categories.
    :rtype: DataFrame
    """
    return sql_context_.createDataFrame(
        cleaned_skills_and_jobs_categories_, ["skill", "job_category"]
    )


def __count_how_often_skill_occur_per_job_category(
    skills_and_jobs_categories_df_: DataFrame,
) -> DataFrame:
    """
    :param skills_and_jobs_categories_df_: DF which contains skills & job categories
    :type skills_and_jobs_categories_df_: DataFrame
    :return: grouped df by job category and skill with additional column that contains value
    how often skill occur per job category
    :rtype: DataFrame
    """
    return (
        skills_and_jobs_categories_df_.groupBy(["job_category", "skill"])
        .count()
        .withColumnRenamed("count", "distinct_skill")
        .sort(desc("count"))
    )


def __save_counted_skills_into_s3_bucket(
    grouped_skills_: DataFrame,
) -> NoReturn:
    """
    Save grouped_skills_ in .csv format into S3 bucket. Later this saved data will be used to show
    bars chart over time.
    :param grouped_skills_: grouped df by job category and skill with additional column that
    contains value how often skill occur per job category
    :type grouped_skills_: DataFrame
    """
    grouped_skills_.repartition(1).write.format(
        "com.databricks.spark.csv"
    ).save(
        path="s3://skills-finder-storage/data/most_wanted_skills",
        mode="overwrite",
    )


if __name__ == "__main__":
    (
        SPARK_SESSION,
        SPARK_CONTEXT,
        SPARK_STREAMING,
        SQL_CONTEXT,
    ) = create_pyspark_operators()
    unstructured_skills_and_jobs_categories: RDD = (
        __load_csv_from_bucket_into_rdd(SQL_CONTEXT)
    )
    skills_and_jobs_categories_without_punctuation: RDD = (
        unstructured_skills_and_jobs_categories.map(
            __remove_punctuation_from_rdd
        )
    )
    cleaned_skills_and_jobs_categories: RDD = (
        __remove_whitespaces_and_no_tech_words_from_rdd(
            skills_and_jobs_categories_without_punctuation, SPARK_SESSION
        )
    )
    skills_and_jobs_categories_df: DataFrame = __transform_cleaned_rdd_into_df(
        cleaned_skills_and_jobs_categories, SQL_CONTEXT
    )
    skill_occur_per_job_category: RDD = (
        __count_how_often_skill_occur_per_job_category(
            skills_and_jobs_categories_df
        )
    )
    __save_counted_skills_into_s3_bucket(skill_occur_per_job_category)
    SPARK_SESSION.stop()
