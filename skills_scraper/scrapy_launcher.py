# !/usr/bin/env python3

"""
Run skills scraper in AWS Lambda and upload results to S3 bucket.
"""

# PSL
import functools
from typing import NoReturn

# Third part
from boto3 import resource
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Own
from skills_scraper.spiders.skills_scraper import SkillsSpider


def show_scrapy_status(scrapper):
    @functools.wraps(scrapper)
    def wrapper():
        print(14 * "-", "SKILLS SCRAPING STARTED!", 14 * "-")
        scrapper()
        print(
            f"SCRAPED {sum(1 for _ in open('/tmp/skills.csv', 'rb'))} SKILLS!"
        )
        print(14 * "-", "SKILLS SCRAPING FINISHED!", 14 * "-")

    return wrapper


@show_scrapy_status
def __start_up_crawler():
    """
    Load config & run spiders.
    """
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(SkillsSpider, jobs_profiles=["backend", "big-data"])
    process.start()


def __upload_file_to_s3_bucket() -> NoReturn:
    """
    When skills scraper end scraping process, all scraped skill will be
    uploaded to s3 bucket.
    """
    s3 = resource("s3")
    s3.Bucket("skills-finder-storage").upload_file(
        "/tmp/skills.csv", "data/scraped_skills/skills.csv"
    )


def invoke_lambda_handler(event, context) -> NoReturn:
    """
    Called by lambda handler.
    """
    __start_up_crawler()
    __upload_file_to_s3_bucket()
