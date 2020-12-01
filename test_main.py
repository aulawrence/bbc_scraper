import datetime
import unittest
import readability
from scrapy.http import TextResponse
from main import BBCSitemapSpider, BBCSitemapNewsSpider, BBCNewsSpider
from utils import format_article_readability


def response_from_file(filename, url=None, request=None):
    if url is None:
        url = "http://0.0.0.0/"
    with open(filename, "r") as f:
        return TextResponse(url=url, request=request, body=f.read().encode("utf-8"))


class TestBBCSitemapSpider(unittest.TestCase):
    def test_parse(self):
        spider = BBCSitemapSpider()
        spider.allowed_domains = ["http://0.0.0.0/"]
        spider.parse_node = spider._parse_node

        response = response_from_file("test_html/https-index-com-news.xml")
        target = [
            {"url": "https://www.bbc.com/sitemaps/https-sitemap-com-news-1.xml"},
            {"url": "https://www.bbc.com/sitemaps/https-sitemap-com-news-2.xml"},
            {"url": "https://www.bbc.com/sitemaps/https-sitemap-com-news-3.xml"},
            {"url": "https://www.bbc.com/sitemaps/https-sitemap-com-news-5.xml"},
        ]

        actual = list(spider._parse(response))

        self.assertListEqual(actual, target)


class TestBBCSitemapNewsSpider(unittest.TestCase):
    def test_parse(self):
        spider = BBCSitemapNewsSpider()
        spider.allowed_domains = ["http://0.0.0.0/"]
        spider.parse_node = spider._parse_node

        response = response_from_file("test_html/https-sitemap-com-news-2.xml")
        target0 = {
            "url": "https://www.bbc.com/sport/snooker/54841402",
            "data": {
                "url": "https://www.bbc.com/sport/snooker/54841402",
                "title": "UK Snooker Championship 2020: BBC coverage times, schedule and results",
                "publication_date": datetime.datetime(2020, 11, 30, 11, 10, 53),
            },
        }
        target1 = {
            "url": "https://www.bbc.com/news/technology-55133141",
            "data": {
                "url": "https://www.bbc.com/news/technology-55133141",
                "title": "Microsoft files patent to record and score meetings on body language",
                "publication_date": datetime.datetime(2020, 11, 30, 17, 00, 12),
            },
        }

        actual = list(spider._parse(response))

        self.assertEqual(actual[0], target0)
        self.assertIn(target1, actual)


class TestBBCNewsSpider(unittest.TestCase):
    def test_parse(self):
        spider = BBCNewsSpider()
        spider.allowed_domains = ["http://0.0.0.0/"]

        response = response_from_file("test_html/technology-55133141.html")
        data = {
            "url": "https://www.bbc.com/news/technology-55133141",
            "data": {
                "url": "https://www.bbc.com/news/technology-55133141",
                "title": "Microsoft files patent to record and score meetings on body language",
                "publication_date": datetime.datetime(2020, 11, 30, 17, 00, 12),
            },
        }
        target_keyword = "Microsoft"
        target_readability = 20.0

        actual = spider._parse(response, data=data)
        formatted_article = format_article_readability(actual["article"])
        readability_results = readability.getmeasures(formatted_article, lang="en")

        self.assertEqual(actual["url"], data["url"])
        self.assertEqual(actual["data"]["url"], data["data"]["url"])
        self.assertEqual(actual["data"]["title"], data["data"]["title"])
        self.assertEqual(
            actual["data"]["publication_date"], data["data"]["publication_date"]
        )
        self.assertGreaterEqual(
            readability_results["readability grades"]["FleschReadingEase"],
            target_readability,
        )
        self.assertIn(target_keyword, actual["keywords"])


if __name__ == "__main__":
    unittest.main()
