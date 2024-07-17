from ui import WebCrawlerApp
from PyQt5.QtWidgets import QApplication
import sys
from database import init_db, clear_database
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from spid.spid.spiders.crawling_spider import CrawlingSpider
from scrapy.linkextractors import LinkExtractor
import importlib
import subprocess

"""
TODO
Run this one. This File.
"""
import search
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from spid.spid.spiders.crawling_spider import CrawlingSpider
from scrapy.linkextractors import LinkExtractor
import spid.spid.settings as settings_module
list1 = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13"]
list2 = ["0","1","2","3","4","5"]
search_query2 = search.Search(list1, list2) 
settings = {attr: getattr(settings_module, attr) for attr in dir(settings_module) if not attr.startswith("__")}
process = CrawlerProcess(settings)
process.crawl(CrawlingSpider, search_query=search_query2)
process.start()

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
            "items.json": {"format": "json",},
        },
    })
    
def run_spider(settings,search_query2):
    process = CrawlerProcess(settings)
    process.crawl(CrawlingSpider, search_query=search_query2)
    process.start()

#process.crawl(CrawlSpider)
#process.start()
#end of spider Running---------------------------------------------------------------------!

###
#process.crawl(CrawlingSpider, fullname="Hello", hometown="Michael")
#process.start()

if __name__ == '__main__':
    main()
    print("moo")
        
