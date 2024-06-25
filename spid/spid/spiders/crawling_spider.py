from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv2 as query
import search
import database as db

class CrawlingSpider(CrawlSpider):
    name = "spidey"
    #allowed_domains = ["whitepages.com", 'privateeye.com', '.com'
    def __init__(self, search_query=None, *args, **kwargs):
        self.search_query = search_query
        self.start_urls = []
        urls = query.get_URLs_from_file("formattedSearchURLs.txt")
        for url in urls:
            moo = query.fill_in_URL(url, search_query)
            self.start_urls.append(f"{moo}")
        
        # Setting rules dynamically based on the provided search query
        self.rules = (
            Rule(LinkExtractor(allow=()), callback='parse_item', follow=True),
        )
        
        super(CrawlingSpider, self).__init__(*args, **kwargs)
        self._compile_rules()

    def parse_item(self, response):
        document = search.Document(response.url)
        document.info = query.highlight_names2(query.extract_text_from_html2(document.url, self.search_query))
        query.updateRelevance(self.search_query, document)
        if document.info:
            db.save_document_to_db(document)
        
        address = response.css("div.addressline-1").get()
        relative = response.css("div.size-aware-h5.fw-m.primary--text").get()

        yield {
            "url": response.url,
            "address": address,
            "relative": relative,
        }
