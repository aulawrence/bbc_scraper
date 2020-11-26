import datetime
import logging
import lxml
import scrapy
from scrapy.utils.log import configure_logging
from lxml.html.clean import Cleaner
from scrapy.crawler import CrawlerProcess
from config import SITEMAP_URL_NEWS, SCRAPPER_LOG_FILE
from database import create_client, destroy_client, insert_news

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename=SCRAPPER_LOG_FILE, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BBCSitemapSpider(scrapy.spiders.XMLFeedSpider):
    name = "bbc_sitemap_spider"

    allowed_domains = ["www.bbc.com"]
    start_urls = [SITEMAP_URL_NEWS]

    iterator = "iternodes"
    namespaces = [
        ("ns", "http://www.sitemaps.org/schemas/sitemap/0.9"),
    ]
    itertag = "sitemap"

    def __init__(self):
        super(BBCSitemapSpider, self).__init__()
        self.sitemap_news_spider = BBCSitemapNewsSpider()

    def parse_node(self, response, selector):
        if len(selector.xpath("ns:loc")) == 1:
            loc = selector.xpath("ns:loc/text()").extract_first()
            yield scrapy.Request(url=loc, callback=self.sitemap_news_spider.parse)


class BBCSitemapNewsSpider(scrapy.spiders.XMLFeedSpider):
    name = "bbc_sitemap_news_spider"

    allowed_domains = ["www.bbc.com"]
    start_urls = []

    iterator = "iternodes"
    namespaces = [
        ("ns", "http://www.sitemaps.org/schemas/sitemap/0.9"),
        ("news", "http://www.google.com/schemas/sitemap-news/0.9"),
    ]
    itertag = "url"

    def __init__(self):
        super(BBCSitemapNewsSpider, self).__init__()
        self.bbc_news_spider = BBCNewsSpider()

    def parse_node(self, response, node):
        if (
            len(node.xpath("ns:loc")) == 1
            and len(node.xpath("news:news/news:publication/news:language")) == 1
            and len(node.xpath("news:news/news:title")) == 1
            and len(node.xpath("news:news/news:publication_date")) == 1
            and node.xpath(
                "news:news/news:publication/news:language/text()"
            ).extract_first()
            == "en"
        ):
            loc = node.xpath("ns:loc/text()").extract_first()
            title = node.xpath("news:news/news:title/text()").extract_first()
            publication_date = node.xpath(
                "news:news/news:publication_date/text()"
            ).extract_first()

            yield scrapy.Request(
                url=loc,
                callback=self.bbc_news_spider.parse,
                cb_kwargs={
                    "data": {
                        "url": loc,
                        "title": title,
                        "publication_date": datetime.datetime.strptime(
                            publication_date, "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    }
                },
            )

    def parse(self, response, **kwargs):
        return self._parse(response, **kwargs)


class BBCNewsSpider(scrapy.Spider):
    name = "bbc_news_spider"

    allowed_domains = ["www.bbc.com"]
    start_urls = []

    def __init__(self):
        super(BBCNewsSpider, self).__init__()
        self.html_cleaner = Cleaner(style=True)
        self.db_client = create_client()

    def start_requests(self):
        for url, data in self.start_urls:
            yield scrapy.Request(url=url, cb_kwargs={"data": data})

    def parse(self, response, **kwargs):
        data = kwargs["data"]
        try:
            article = response.xpath("//article")[0]
        except IndexError:
            self.logger.warning("Article not found. Url: {}".format(data["url"]))
            return
        article_ls = []
        keyword_ls = []
        for component_html in article.xpath(
            "div[not(@data-component='media-block' or @data-component='image-block' or @data-component='tag-list')]"
        ).extract():
            clean_html = self.html_cleaner.clean_html(component_html)
            tree = lxml.html.fromstring(clean_html)
            article_ls.append(tree.text_content())
        if not article_ls:
            self.logger.warning("Article empty. Url: {}".format(data["url"]))
            return
        for keyword_html in article.xpath(
            "section[@data-component='tag-list']//li"
        ).extract():
            clean_html = self.html_cleaner.clean_html(keyword_html)
            tree = lxml.html.fromstring(clean_html)
            keyword_ls.append(tree.text_content())
        data["article"] = " ".join(article_ls)
        data["keywords"] = keyword_ls
        insert_news(self.db_client, data)

    def closed(self, reason):
        destroy_client(self.db_client)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BBCSitemapSpider)
    process.start()
