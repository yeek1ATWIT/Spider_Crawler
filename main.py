from ui import WebCrawlerApp
from PyQt5.QtWidgets import QApplication
import sys
from database import init_db, clear_database
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from spid.spid.spiders.crawling_spider import CrawlingSpider
from scrapy.linkextractors import LinkExtractor
"""
TODO
Run this one. This File.
"""


def main():
#Run UI
    init_db()
    clear_database()
    app = QApplication(sys.argv)
    ex = WebCrawlerApp()
    ex.show()
    sys.exit(app.exec_())

#run spider--------------------------------------------------------------------------------!
process = CrawlerProcess(settings={
        "FEEDS": {
            "items.json": {"format": "json", 'overwrite': True},
        },
    })

#process.crawl(CrawlSpider)
#process.start()
#end of spider Running---------------------------------------------------------------------!

###
#process.crawl(CrawlingSpider, fullname="Hello", hometown="Michael")
#process.start()

if __name__ == '__main__':
    main()
    print("moo")