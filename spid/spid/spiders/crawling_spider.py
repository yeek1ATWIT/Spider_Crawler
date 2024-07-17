from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv3 as query
import search
import database as db

class CrawlingSpider(CrawlSpider):
    name = "spidey"
    #allowed_domains = ["whitepages.com", 'privateeye.com', '.com']

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

    def update_relevance_score(self, search_query, document, picture_in_document=False):
        document_info_lower = document.info.lower()

        # Tests if name is in document
        if search_query.first_name.value and (search_query.first_name.value.lower() in document_info_lower):
            document.name_relevance_score = search_query.first_name.weight
        elif search_query.middle_name.value and (search_query.middle_name.value.lower() in document_info_lower):
            document.name_relevance_score = search_query.middle_name.weight   
        elif search_query.last_name and (search_query.last_name.value.lower() in document_info_lower):
            document.name_relevance_score = search_query.last_name.weight
        document.relevance_score += document.name_relevance_score

        # Tests if birthday is in document
        if search_query.birthday.value.replace('-', '') and (search_query.birthday.value.lower() in document_info_lower):
            document.birthday_relevance_score = search_query.birthday.weight
        document.relevance_score += document.birthday_relevance_score

        # Tests if phone number is in document
        if search_query.phone_number.value and (search_query.phone_number.value.lower() in document_info_lower):
            document.phone_relevance_score = search_query.phone_number.weight
        document.relevance_score += document.phone_relevance_score

        # Tests if address is in document
        if search_query.street.value and (search_query.street.value.lower() in document_info_lower):
            document.address_relevance_score = search_query.street.weight
        elif search_query.city.value and (search_query.city.value.lower() in document_info_lower):
            document.address_relevance_score = search_query.city.weight
        elif search_query.state.value and (search_query.state.value.lower() in document_info_lower):
            document.address_relevance_score = search_query.state.weight
        document.relevance_score += document.address_relevance_score

        # Tests if zipcode is in document
        if search_query.zipcode.value and (search_query.zipcode.value.lower() in document_info_lower):
            document.zipcode_relevance_score = search_query.zipcode.weight
        document.relevance_score += document.zipcode_relevance_score

        # Tests if picture is in document
        if picture_in_document:
            document.picture_relevance_score = search_query.picture.weight
        document.relevance_score += document.picture_relevance_score


    def parse_item(self, response):
        document = search.Document(response.url)
        document.info = query.highlight_names2(query.extract_text_from_html2(document.url, self.search_query))
        #query.updateRelevance(self.search_query, document)
        self.update_relevance_score(self.search_query, document)
        if document.info:
            db.save_document_to_db(document)
        
        address = response.css("div.addressline-1").get()
        relative = response.css("div.size-aware-h5.fw-m.primary--text").get()

        yield {
            "url": response.url,
            "address": address,
            "relative": relative,
        }
