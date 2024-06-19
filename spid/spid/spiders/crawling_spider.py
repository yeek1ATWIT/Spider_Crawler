from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CrawlingSpider(CrawlSpider):
#this is the identifier of the above class (spider)
    name = "spidey"
#can be activated in terminal via: cd spid
#                            then: scrapy crawl spidey
#domains to search
    allowed_domains = ["whitepages.com", ""]
#where to start
    fullname = "Aidan-D-Gardner"
    hometown = "Hanover-MA"

    start_urls = ["https://www.whitepages.com/name/"]
    PROXY_SERVER = "ip address of proxy server"
    #go to middlewares.py line 82 and paste proxy ip
#rules
    rules = (
#allow links with ...
        Rule(LinkExtractor(allow= fullname + "/" + hometown)),
        Rule(LinkExtractor(allow= fullname, deny= hometown), callback = "parse_item"),
    )

def parse_item(self, response):
    yield {
            "address": response.css("div.addressline-1").get(),
            "relative": response.css("div.size-aware-h5.fw-m.primary--text").get(),


    }
