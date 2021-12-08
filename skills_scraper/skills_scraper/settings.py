"""
All scraper config is located here.
"""

# PSL
from typing import List

LOG_ENABLED: bool = False
ROBOTSTXT_OBEY: bool = False
FEED_FORMAT: str = "csv"
FEED_URI: str = "/tmp/skills.csv"
BOT_NAME: str = "skills_scraper"
NEWSPIDER_MODULE: str = "skills_scraper.spiders"
USER_AGENT: str = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
SPIDER_MODULES: List[str] = ["skills_scraper.spiders"]
