"""
Skills scraper logic.
"""

# PSL
from os import getenv
from pathlib import PurePosixPath
from typing import List, NoReturn
from urllib.parse import unquote, urlparse

# Third part
from dotenv import load_dotenv
from scrapy import Spider, Request


class SkillsSpider(Spider):
    """
    Main skills scraper.
    """

    def __init__(self, *args, **kwargs):
        load_dotenv()
        self.name: str = "skills_scraper"
        self.start_urls: List[str] = [
            f"{getenv('URL_TO_SCRAPE')}{job_profile}?page=1"
            for job_profile in kwargs["jobs_profiles"]
        ]
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_job_category(current_url: str) -> str:
        """
        Get job category from site.
        :param current_url: currently scraped job profile
        :type current_url: str
        :return: job category
        :rtype: str
        """
        return PurePosixPath(unquote(urlparse(current_url).path)).parts[-1]

    def parse(self, response, **kwargs) -> NoReturn:
        """
        Parse data from site with jobs offers.
        """
        for url in response.xpath(
            '*//a[contains(@class, "posting-list-item")]/@href'
        ).getall():
            yield Request(
                response.urljoin(getenv("URL_TO_SCRAPE")[:23] + url),
                callback=self.fetch_skills_from_job_profile,
                meta={
                    "job_category": self.get_job_category(
                        current_url=response.request.url
                    )
                },
            )

        next_page: str = (
            response.css("li.page-item").css("a::attr(href)")[-1].extract()
        )
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def fetch_skills_from_job_profile(response) -> NoReturn:
        """
        From all scraped data per single job profile this function will get only skills.
        Scrapy will save automatically this scraped skills into file (see settings.py).
        """
        for skill in (
            response.css("common-posting-requirements")
            .css("h3")
            .css("common-posting-item-tag")
            .css("button::text")
            .getall()
        ):
            yield {
                "skill": skill.strip(),
                "job_category": response.meta.get("job_category"),
            }
