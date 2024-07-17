import scrapy 
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv2 as query
import search
from spid.spid.items import SpidItem as db
from spid.spid.items import SpidItem
import logging
class CrawlingSpider(Spider):
    name = "spidey"
    allowed_domains = ['whoseno.com']
    #start_urls = ['https://www.whoseno.com/US/']
    custom_settings = {
        'FEEDS': {
            'rawdata.json': {'format': 'json', 'overwrite': True},
        },
        'ROBOTSTXT_OBEY': False 
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
        #self._compile_rules() 

    def parse(self, response):
        """ Default parse method required by Scrapy """
        pass  # This method is intentionally left empty as it's required by scrapy

    def parse_item(self, response):
        document = search.Document(response.url)
        document.info = query.highlight_names2(query.extract_text_from_html2(document.url, self.search_query))
        #query.updateRelevance(self.search_query, document)
        document.info = "sasasasasasasasasasa"
        
        if document.info:
            db.save_document_to_db(document)
        
        self.logger.info(f"Parsing {response.url}")
        self.logger.info(f"Name: {response.css('b::text').get()}")
        self.logger.info(f"Phone: {response.css('h1::text').get()}")

        name = response.css('b::text').get()
        phone = response.css('h1::text').get()

        # Handling potential None values from CSS selectors
        name = name.strip() if name else None
        phone = phone.strip() if phone else None

        # Creating and yielding item
        spid_item = SpidItem()
        spid_item['url'] = response.url
        spid_item['name'] = name
        spid_item['phone'] = phone

        yield spid_item
