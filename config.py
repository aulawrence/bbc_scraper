import scrapy
import logging
from scrapy.utils.log import configure_logging

SITEMAP_URL_NEWS = "https://www.bbc.com/sitemaps/https-index-com-news.xml"
DATABASE_URL = "mongodb://localhost"
DATABASE_PORT = 27017
DATABASE_NAME = "bbc_scraper"
LOG_FILE = "log.txt"

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s"
)