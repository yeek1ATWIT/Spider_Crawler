import scrapy 
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv2 as query
import search
from spid.spid.items import SpidItem as db
from spid.spid.items import SpidItem

class CrawlingSpider(Spider):
    name = "spidey"
    allowed_domains = ['whoseno.com/US']
    start_urls = ['https://www.whoseno.com/US/']
    custom_settings = {
        'FEEDS': {
            'rawdata.json': {'format': 'json', 'overwrite': True},
        }
    }

    def __init__(self, search_query=None, *args, **kwargs):
        super(CrawlingSpider, self).__init__(*args, **kwargs)
        self.search_query = search_query
        self.start_urls = []
        urls = query.get_URLs_from_file("formattedSearchURLs.txt")
        
        for url in urls:
            filled_url = query.fill_in_URL(url, search_query)
            self.start_urls.append(filled_url)
        
        # Setting rules dynamically based on the provided search query
        self.rules = [
            Rule(LinkExtractor(allow=()), callback='parse_item', follow=True),
        ]
        
    def parse_item(self, response):
        document = search.Document(response.url)
        document.info = query.highlight_names2(query.extract_text_from_html2(document.url, self.search_query))
        query.updateRelevance(self.search_query, document)
        
        if document.info:
            db.save_document_to_db(document)
        
        # Splitting yields for each website
        spid_item = SpidItem()

        spid_item['url'] = response.url,
        spid_item['name'] = response.css('b').get(),
        spid_item['phone'] = response.css('h1').get(),
        
        yield SpidItem

# Code Graveyard
# address = response.css("div.addressline-1").get()
# relative = response.css("div.size-aware-h5.fw-m.primary--text").get()
# firstName = response.css("div.addressline-1").get()
# middleName = response.css("div.addressline-1").get()
# lastName = response.css("div.addressline-1").get()
# birthDay = response.css("div.addressline-1").get()
# birthMonth = response.css("div.addressline-1").get()
# birthYear = response.css("div.addressline-1").get()
# phone = response.css("div.addressline-1").get()
# age = response.css("div.addressline-1").get()
# street = response.css("div.addressline-1").get()
# city = response.css("div.addressline-1").get()
# aprt = response.css("div.addressline-1").get()
# hometown = response.css("div.addressline-1").get()
# relative =  response.css("div.addressline-1").get()
#
# yield {
#     "url": response.url,
#     "address": address,
#     "relative": relative,
# }
