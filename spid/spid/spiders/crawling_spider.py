from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
import queryURLsv3 as query
import search
import database as db
from bs4 import BeautifulSoup
import json
import csv
from collections import defaultdict

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
            def get_css_selector(tag):
                path = []
                while tag is not None:
                    name = tag.name
                    if name == '[document]':
                        break
                    # Add the tag name to the path
                    path.append(name)
                    tag = tag.parent
                return ' > '.join(path[::-1])
            result = []
            text = tag.get_text(separator='\n').strip()
            css_selector = get_css_selector(tag)

            if text:
                if tag.get('class') is None:
                    result.append(' '.join(text.split())+' |||'+str(css_selector).replace(" ", "")+str([tag.get(attr) for attr in tag.attrs.keys()]))
                elif tag.get('class') is list or tag.get('class') is dict:
                    result.append(' '.join(text.split())+' |||'+str(css_selector).replace(" ", "")+str([tag.get(attr) for attr in tag.attrs.keys()]).replace(" ", ""))
                else: 
                    result.append(' '.join(text.split())+' |||'+str(css_selector).replace(" ", "")+str([tag.get(attr) for attr in tag.attrs.keys()]).replace(" ", ""))
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
        hardcoded_urls = list(query.get_URLs_from_file("hardcodedURLs2.txt"))
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

    def getAddressCSV(self):
        state_to_cities = defaultdict(lambda: {'code': '', 'cities': set()})
        city_to_states = defaultdict(list)

        with open('csv/kelvins/us_cities.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                state_name = row['STATE_NAME']
                state_code = row['STATE_CODE']
                city = row['CITY']

                state_to_cities[state_name]['code'] = state_code
                state_to_cities[state_name]['cities'].add(city)
                city_to_states[city].append((state_name, state_code))

        states = list(state_to_cities.keys())
        state_codes = [info['code'] for info in state_to_cities.values()]
        cities = list(city_to_states.keys())

        state_to_cities = {state: {'code': info['code'], 'cities': list(info['cities'])} for state, info in state_to_cities.items()}

        return states, state_codes

    def is_words_in_list(self, words, _list):
        if isinstance(words, str):
            words = words.split(" ")
        if isinstance(_list, str):
            _list = _list.split(" ")
        if isinstance(words, list):
            for word in words:
                if word.lower() in [x.lower() for x in _list]:
                    return True
        return False

        
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
        
        hardcoded_urls = query.get_URLs_from_file("hardcodedURLs2.txt")

        jeff =  any(s.split(" ", 1)[0].replace("https://", "").replace("http://", "").replace("www.", "") in stur for s in hardcoded_urls)

        stur = response.url.replace("https://", "").replace("http://", "").replace("www.", "") 
        
        if jeff: #and not self.already_done:
            self.already_done = True
            hardcoded_stuff = self.ishardcoded(response.url)
            words = hardcoded_stuff.split(' ')
            table = self.extract_text_from_html2(response.text)

            name2 = json.loads(words[1])
            phone2 = json.loads(words[2])
            address2 = json.loads(words[3])
            age2 = json.loads(words[4])

            def find(indexes):
                output = ""
                for index in indexes:
                    output += "INDEX "+str(index)+": "
                    output += table[int(index)].split(": ", 1)[1]
                    output += "\n"
                return output
            
            def findClassForAge(classes):
                output = ""
                for _class in classes:
                    for item in table:
                        test_item = item.split(": ", 1)[1].split("|||", 1)[1]
                        html_stuff = item.split(": ", 1)[1].split("|||", 1)[0]
                        numbers = sum(c.isdigit() for c in html_stuff)
                        if _class == test_item and numbers > 0 and html_stuff.count(" ") < 10 and "None" not in _class and "\'" in _class and item.split(": ", 1)[1].split("|||", 1)[0] not in output:
                            output += html_stuff
                            output += '\n'
                return output
            
            def findClassForName(classes):
                output = ""
                states, state_codes = self.getAddressCSV()
                for _class in classes:
                    for item in table:
                        test_item = item.split(": ", 1)[1].split("|||", 1)[1]
                        html_stuff = item.split(": ", 1)[1].split("|||", 1)[0]
                        if _class == test_item and len(html_stuff) > 3 and html_stuff.count(" ") < 8 and not self.is_words_in_list(html_stuff, states) and not self.is_words_in_list(html_stuff, state_codes) and "None" not in _class and "\'" in _class and item.split(": ", 1)[1].split("|||", 1)[0] not in output:
                            output += html_stuff
                            output += '\n'
                return output
            
            def findClassForPhone(classes):
                output = ""
                for _class in classes:
                    for item in table:
                        test_item = item.split(": ", 1)[1].split("|||", 1)[1]
                        html_stuff = item.split(": ", 1)[1].split("|||", 1)[0]
                        numbers = sum(c.isdigit() for c in html_stuff)
                        if _class == test_item and numbers > 8 and html_stuff.count(" ") < 4 and "None" not in _class and "\'" in _class and item.split(": ", 1)[1].split("|||", 1)[0] not in output:
                            output += html_stuff
                            output += '\n'
                return output

            def findClassForAddress(names, classes):
                output = ""
                
                for _class in classes:
                    for item in table:
                        test_item = item.split(": ", 1)[1].split("|||", 1)[1]
                        html_stuff = item.split(": ", 1)[1].split("|||", 1)[0]
                        numbers = sum(c.isdigit() for c in html_stuff)
                        if _class == test_item and not self.is_words_in_list([i for i in names.replace("\n", " ").split(" ") if (len(i) > 1 and not ":" in i)], html_stuff) and numbers < 8 and html_stuff.count(" ") < 15 and "None" not in _class and "\'" in _class and item.split(": ", 1)[1].split("|||", 1)[0] not in output:
                            output += html_stuff
                            output += '\n'
                return output

            # Flip to false if all things have been converted from index to class
            switch = False
            if switch:
                result = "ALREADY HARDCODED!\n"
                result += "Name:\n"+find(name2)
                result += "Phone:\n"+find(phone2)
                result += "Address:\n"+find(address2)
                result += "Age:\n"+find(age2)
            else:
                result = "ALREADY HARDCODED!\n"
                result += response.url+"\n"
                result += "Name:\n"+findClassForName(name2)
                result += "Phone:\n"+findClassForPhone(phone2)
                result += "Address:\n"+findClassForAddress(result, address2)
                result += "Age:\n"+findClassForAge(age2)

            g = open("hardcodedOutput.txt", "w")
            g.write(result)
            g.close() 

            """
            # Swaps Index for Class
            def getClass(indexes):
                output = "["
                for index in indexes:
                    output += "\""+str(table[int(index)].split('|||', 1)[1]) + "\""
                    output += ','
                output = output[:-1]
                output += '] '
                if output == '] ':
                    return '[] '
                return output

            result2 = ""
            result2 += response.url + " "
            result2 += getClass(name2)
            result2 += getClass(phone2)
            result2 += getClass(address2)
            result2 += getClass(age2)
            
            f = open("hardcodedURLs2.txt", "a")
            f.write(result2+"\n")
            f.close()
            """
            
            
            
        elif any(stur in s for s in urls) and not self.already_done:
            f = open("hardcodedOutput.txt", "w")
            f.write(document.info.replace("<br>", "\n"))
            f.close()

