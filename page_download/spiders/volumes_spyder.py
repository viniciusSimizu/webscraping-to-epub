import shelve
from urllib.parse import urlparse
import scrapy.http


class VolumesSpyder(scrapy.Spider):
    name = "volumes"
    start_urls = ["https://www.animecenterbr.com/youkoso-jitsuryoku-light-novel-pt-br/"]
    allowed_domains = ["animecenterbr.com"]

    def parse(self, response):
        with shelve.open("pages") as db:
            db.setdefault(urlparse(response.url).path, response.text)

        chapters = response.css(".post-text-content a")

        yield from response.follow_all(chapters, callback=self.parse_chapter)

    def parse_chapter(self, response: scrapy.http.Response):
        with shelve.open("pages") as db:
            db[urlparse(response.url).path] = response.text
