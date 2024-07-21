from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv3 as query
import search
import database as db
from bs4 import BeautifulSoup
import json

class CrawlingSpider(Spider):

    name = "spidey"

    #allowed_domains = ["whitepages.com", 'privateeye.com', '.com']
    
    def __init__(self, search_query=None, *args, **kwargs):
        self.search_query = search_query
        self.start_urls = []
        urls = query.get_URLs_from_file("formattedSearchURLs.txt")
        
        # TODO README
        # YOU CAN SET 'enableInput' TO TRUE OR FALSE
        # IF TRUE, IT ADLIBS THE URLS ON "formattedSearchURLs.txt"
        # IF FALSE, IT USES THE URLS ON "formattedSearchURLs.txt" DIRECTLY
        # RIGHT NOT IT'S SET TO FALSE, SO IT'S NOT READING ANY CREDENTIALS SUBMITTED TO THE UI
        enableInput = False
        if enableInput:
            for url in urls:
                moo = query.fill_in_URL(url, search_query)
                self.start_urls.append(f"{moo}")
        else:
            for url in urls:
                self.start_urls.append(f"{url}")
        #----------------------------------------------#
        """
        # Setting rules dynamically based on the provided search query
        self.rules = (
            Rule(LinkExtractor(allow=()), callback='parse', follow=True),
        )
        
        super(CrawlingSpider, self).__init__(*args, **kwargs)
        self._compile_rules()
        """
        self.already_done = False

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

    def extract_text_from_html2(self, text):
        try:
            soup = BeautifulSoup(text, 'html.parser')
        except:
            return []

        def extract_text(tag):
            result = []
            text = tag.get_text(separator='\n').strip()
            if text:
                result.append(' '.join(text.split()))
            for child in tag.children:
                if child.name:
                    result.extend(extract_text(child))
            return result

        def flatten_list(nested_list):
            return [item for sublist in nested_list for item in (flatten_list(sublist) if isinstance(sublist, list) else [sublist])]

        text_list = []
        html_tags = [
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "span", "strong", "em", "b", "i",
            "div", "section", "article", "header", "footer", "aside",
            "ul", "ol", "li",
            "table", "tr", "td", "th",
            "a", "td", "tr"
            "dl", "dt", "dd",
            "address", "figure", "figcaption"
        ]
        for tag in soup.find_all(html_tags):
            text_list.extend(extract_text(tag))

        flat_list = flatten_list(text_list)
        result = []
        for i in range(len(flat_list)):

            result.append("INDEX "+str(i)+": "+flat_list[i])
        return result

    def ishardcoded(self, url):
        hardcoded_urls = list(query.get_URLs_from_file("hardcodedURLs.txt"))
        #if "website.com" in hardcoded_urls[0]:
        #    hardcoded_urls.remove() # Removes sample
        compare_urls = []
        result = []

        stur = url.replace("https://", "").replace("http://", "").replace("www.", "")   
        for hardcoded_url in hardcoded_urls:
            hardcoded_url_format = hardcoded_url.split(" ", 1)[0].replace("https://", "").replace("http://", "").replace("www.", "")
            if hardcoded_url_format in stur:
                compare_urls.append(hardcoded_url.split(' ', 1)[0])
                result.append(hardcoded_url)
        if compare_urls:
            r_index = compare_urls.index(min(compare_urls, key=len))
        
        if result:
            return result[r_index]
        
        return None
        
    def parse(self, response):
        document = search.Document(response.url)
        document.info = query.highlight_names2(query.extract_text_from_html2(document.url, self.search_query))
        #query.updateRelevance(self.search_query, document)
    
        # HERE'S THE NAME AND PHONE IF YOU STILL WANT IT
        name = response.css('b::text').get()
        phone = response.css('h1::text').get()
        if name and phone:
            document.info = "Name: "+name+"<br>Phone: "+phone
        if name:
            document.info = "Name: "+name+"<br>Phone: "
        if phone:
            document.info = "Name: "+"<br>Phone: "+phone
        else:
            document.info = "Name: "+"<br>Phone: "
        document.info += '<br>'
        #---------------------------------------------#

        document.info += '<br>'.join(self.extract_text_from_html2(response.text))

        ## NOTE FOR ME THIS IS REAL CODE
        self.update_relevance_score(self.search_query, document)
        if document.info:
            db.save_document_to_db(document)
        ##--------------------------------

        # HARDCODED CODE
        urls = query.get_URLs_from_file("formattedSearchURLs.txt")
        stur = response.url.replace("https://", "").replace("http://", "").replace("www.", "") 
        
        hardcoded_urls = query.get_URLs_from_file("hardcodedURLs.txt")

        jeff =  any(s.split(" ", 1)[0].replace("https://", "").replace("http://", "").replace("www.", "") in stur for s in hardcoded_urls)

        stur = response.url.replace("https://", "").replace("http://", "").replace("www.", "") 
        
        if jeff and not self.already_done:
            self.already_done = True
            hardcoded_stuff = self.ishardcoded(response.url)
            words = hardcoded_stuff.split(' ')
            table = self.extract_text_from_html2(response.text)

            name2 = json.loads(words[1])
            phone2 = json.loads(words[2])
            address2 = json.loads(words[3])

            def find(indexes):
                output = ""
                for index in indexes:
                    output += "INDEX "+str(index)+": "
                    output += table[int(index)].split(": ", 1)[1]
                    output += "\n"
                return output
            result = "ALREADY HARDCODED!\n"
            result += "Name:\n"+find(name2)
            result += "Phone:\n"+find(phone2)
            result += "Address:\n"+find(address2)

            g = open("hardcodedOutput.txt", "w")
            g.write(result)
            g.close() 
            
        elif any(stur in s for s in urls) and not self.already_done:
            f = open("hardcodedOutput.txt", "w")
            f.write(document.info.replace("<br>", "\n"))
            f.close()

