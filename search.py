import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import httpx
import database as db
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import queryURLsv3 as queryURLs
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from spid.spid.spiders.crawling_spider import CrawlingSpider
from scrapy.linkextractors import LinkExtractor
import spid.spid.settings as settings_module


class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_numbers = []
        self.addresses = []
        self.family_members = []

class Document:
    def __init__(self, url):
        self.url = url
        self.info = ''
        self.name_relevance_score = 0
        self.birthday_relevance_score = 0
        self.phone_relevance_score = 0
        self.address_relevance_score = 0
        self.zipcode_relevance_score = 0
        self.picture_relevance_score = 0
        self.relevance_score = 0

class SearchEntry:
    def __init__(self, value, weight):
        self.value = value
        self.weight = weight

class Search:
    def __init__(self, input, weight):
        self.first_name = SearchEntry(input[0], weight[0])
        self.middle_name = SearchEntry(input[1], weight[0])
        self.last_name = SearchEntry(input[2], weight[0])
        self.birthday = SearchEntry(input[3]+"-"+input[4]+"-"+input[5], weight[1])
        self.phone_number = SearchEntry(input[6]+input[7]+input[8], weight[2])
        self.street = SearchEntry(input[9], weight[3])
        self.city = SearchEntry(input[10], weight[3])
        self.state = SearchEntry(input[11], weight[3])
        self.zipcode = SearchEntry(input[12], weight[4])
        self.picture = SearchEntry(input[13], weight[5])

    def get_all_entries(self):
        return [attr for attr in self.__dict__.values()]
    
    def get_all_entries_except_picture(self):
        return [attr for name, attr in self.__dict__.items() if name != 'picture']

    
    

"""
TODO
Ignore my messy code, there's a bunch of messy comments, naming conventions, etc..
I'll probably clean it up.

Anyways, SearchType0 through 4 have entirely different approaches to scanning the
internet. I implemented SearchType1 because I wanted to create a prototype, that
leaves SearchType0, 2, 3, 4 empty. The order doesn't really matter, and I created
4 empty slots just in case you wanted to do something. I can delete the unused ones
later. 

The UI submit button calls the SeachTypes search function: search(self, search_query)
so you probably shouldn't delete it. @param search_query is a search class; you can
access search text (for example) via search_query.first_name.value and 
search_query.first_name.weight for weight. Yes, the picture/upload head thing works,
you can drag an image on the thing and submit it. You can change the AI text via the 
command "self.update_ai_text("Insert thing here")".

Do whatever- especially with this file.
"""
class SearchType0:
    def search(self, search_query2):
        # Convert the settings module to a dictionary
        settings = {attr: getattr(settings_module, attr) for attr in dir(settings_module) if not attr.startswith("__")}
        from main import run_spider
        run_spider(settings,search_query2)
        
        #print("SearchType0 Activated!\n")
        #self.update_ai_text("HI!")

class SearchType1:
    def calculate_relevance(document_text, inputs, weights):
        relevance_score = 0
        for term, weight in zip(inputs, weights):
            if term.lower() in document_text.lower():
                relevance_score += weight
        return relevance_score


    def extract_info_from_html(html):
        soup = BeautifulSoup(html, 'html.parser')
        phone_numbers = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', soup.get_text())
        addresses = re.findall(r'\d+\s+\w+\s+\w+', soup.get_text())

        return phone_numbers, addresses

    def reverse_image_search(image_bytes):
        search_url = 'https://www.google.com/searchbyimage/upload'
        files = {'encoded_image': ('image.png', image_bytes)}
        response = requests.post(search_url, files=files)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.select('a[href^="/imgres"]')

        return results

    def process_url(url, inputs, weights):
        try:
            response = requests.get(url)

            document_text = response.text

            phone_numbers, addresses = SearchType1.extract_info_from_html(document_text)

            document = Document(url)
            document.info = "Hi"
            #document.relevance_score = SearchType1.calculate_relevance(document_text, inputs, weights)
            document.relevance_score=2
            db.save_document_to_db(document)
        except Exception as e:
            print(f"Failed to fetch or parse {url}: {e}\n")
            
    def open_and_close_url_with_selenium(url):
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1,1")
        options.add_argument("--window-position=1000,1000")
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1, 1)
        driver.minimize_window()
        driver.get(url)
        driver.implicitly_wait(2)
        driver.quit()
        print(f"Closed {url}")

    def fetch_html(url):
        if "dogpile.com" in url:
            SearchType1.open_and_close_url_with_selenium(url)
        if "duckduckgo.com" in url:
            SearchType1.open_and_close_url_with_selenium(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        client = httpx.Client(headers=headers, follow_redirects=True, http2=True)
        try:
            response = client.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch {url} with status code {response.status_code}\n")
                #webbrowser.open(url)
                #input("Press Enter to continue...")
                return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {url}: {e}\n")
            return None
        finally:
            client.close()

    def parse_html(html, tag, attribute):
        exclude_list = [
            "startpage",
            "system1",
            "bing",
            "StartpageSearch",
            "infospace.com"
        ]
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all(tag, attrs=attribute)
            urls = []
            for link in links:
                href = link.get('href')
                if href:
                    if not any(exclude in href for exclude in exclude_list):
                        urls.append(href)
            return urls
        except:
            return []

    def unique_domains(urls):
        unique = []
        seen_domains = set()
        for url in urls:
            domain = urlparse(url).netloc
            if domain not in seen_domains:
                seen_domains.add(domain)
                unique.append(url)
        return unique
    
    def fill_and_submit_form(url, search):
        # Set up the WebDriver (make sure you have the appropriate driver installed and in your PATH)
        driver = webdriver.Chrome()

        try:
            # Navigate to the URL
            driver.get(url)

            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Get the page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Define potential input field identifiers
            input_identifiers = {
                'first_name': ['first_name', 'firstname', 'First Name', 'FirstName'],
                'middle_name': ['middle_name', 'middlename', 'Middle Name', 'MiddleName'],
                'last_name': ['last_name', 'lastname', 'Last Name', 'LastName'],
                'address': ['address', 'Address'],
                'city': ['city', 'City'],
                'state': ['state', 'State'],
                'zipcode': ['zipcode', 'Zipcode', 'zip_code', 'Zip Code', 'Postal Code', 'postal_code']
            }

            # Find and fill input fields
            def find_and_fill_input(field, value):
                for identifier in input_identifiers[field]:
                    try:
                        input_element = driver.find_element(By.NAME, identifier)
                        input_element.send_keys(value)
                        return True
                    except NoSuchElementException:
                        try:
                            input_element = driver.find_element(By.ID, identifier)
                            input_element.send_keys(value)
                            return True
                        except NoSuchElementException:
                            try:
                                input_element = driver.find_element(By.CSS_SELECTOR, f"[title='{identifier}']")
                                input_element.send_keys(value)
                                return True
                            except NoSuchElementException:
                                try:
                                    input_element = driver.find_element(By.CSS_SELECTOR, f"[placeholder='{identifier}']")
                                    input_element.send_keys(value)
                                    return True
                                except NoSuchElementException:
                                    continue
                print("false")
                return False

            # Fill out the form fields
            find_and_fill_input('first_name', search.first_name.value)
            find_and_fill_input('last_name', search.last_name.value)
            find_and_fill_input('address', search.address.value)
            find_and_fill_input('city', search.address.value.split(" ")[1])

            # Find the submit button and click it
            submit_button_identifiers = ['submit', 'enter', 'search', 'go', 'search now', 'Search now']

            def find_and_click_button():
                for identifier in submit_button_identifiers:
                    try:
                        button = driver.find_element(By.NAME, identifier)
                        button.click()
                        return True
                    except NoSuchElementException:
                        try:
                            button = driver.find_element(By.ID, identifier)
                            button.click()
                            return True
                        except NoSuchElementException:
                            try:
                                button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary') and contains(@class, 'btn-custom') and contains(@class, 'btn-block')]")
                                button.click()
                                return True
                            except NoSuchElementException:
                                continue
                return False

            if not find_and_click_button():
                raise Exception('Submit button not found')

            # Wait for the next page to load and get the new URL
            time.sleep(1) 
            new_url = driver.current_url

            print(f"New URL: {new_url}")

        finally:
            # Close the browser
            driver.quit()
            
    def search_bing(query, page=1):
        if page == 1:
            url = f"https://www.bing.com/search?q={query}&PC=U316&FORM=CHROMN"
        else:
            offset = (page - 1) * 10 + 1
            url = f"https://www.bing.com/search?q={query}&first={offset}&PC=U316&FORM=CHROMN"
        return url

    def search_dogpile(query, page=1):
        if page == 1:
            url = f"https://www.dogpile.com/search/web?q={query}"
        else:
            url = f"https://www.dogpile.com/search/web?q={query}&page={page}"
        return url

    def search_duckduckgo(query, page=1):
        if page == 1:
            url = f"https://duckduckgo.com/html/?q={query}"
        else:
            offset = (page - 1) * 30
            url = f"https://duckduckgo.com/html/?q={query}&s={offset}"
        return url

    def search_startpage(query, page=1):
        url = f"https://www.startpage.com/do/search?q={query}&page={page}"
        return url

    def search_all_engines(query):
        links = {
            SearchType1.search_bing(query, 1),
            #SearchType1.search_dogpile(query, 1),
            #SearchType1.search_duckduckgo(query, 1),
            SearchType1.search_startpage(query, 1),
            SearchType1.search_bing(query, 2),
            #SearchType1.search_duckduckgo(query, 2),
            SearchType1.search_startpage(query, 2),
            SearchType1.search_bing(query, 3),
            #SearchType1.search_duckduckgo(query, 3),
            SearchType1.search_startpage(query, 3)
        }
        results = []
        for link in links: 
            results.extend(SearchType1.parse_html(SearchType1.fetch_html(link), 'a', {'href': True}))
        return results

    def search(self, search_query):
        """
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async query function in the event loop
        try:
            loop.run_until_complete(queryURLs.query(search_query))
        finally:
            loop.close()
        """
        documents = queryURLs.query(search_query)
        """
        for document in documents:
            #document.info = document.info.replace('\n', '<br>')
            document.info = SearchType1.highlight_names(document.info, search_query.first_name.value, search_query.last_name.value)
            db.save_document_to_db(document)
        return
        """
        """
        #try:
            inputs = []
            weights = []
            query_values = search_query.get_all_entries()

            for i in range(9):
                inputs.append(query_values[i].value)
                weights.append(query_values[i].weight if query_values[i].value else 0)
        
        
            #run_spider(' '.join(inputs))
            '''
            # Perform parallel processing of URLs
            search_results = googlesearch.search(' '.join(inputs), num_results=100)
            #search_results = search_with_selenium(' '.join(inputs), num_results=100)
            
            if query_values[6].value:
                image_results = reverse_image_search(query_values[6].value)
                index = 0
                for item in image_results:
                    index = random.randint(index, min(index+2, len(search_results)))
                    search_results.insert(index, item)
            '''
            SearchType1.fill_and_submit_form("https://www.privateeye.com/", search_query)

            search_results = SearchType1.search_all_engines(' '.join(inputs))
            with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
                futures = [executor.submit(SearchType1.process_url, url, inputs, weights) for url in search_results]
                #futures = [executor.submit(selenium_process_url, url, inputs, weights) for url in search_results]

            for future in futures:
                future.result()

            if not self.searching_flag:
                return
            #'''
        #except:
         #   print(f"An error occurred while threading SearchType1")
"""

class SearchType2:
    def search(self, search_query):
        print("SearchType2 Activated!\n")
        self.update_ai_text("HI!")

class SearchType3:
    def search(self, search_query):
        print("SearchType3 Activated!\n")
        self.update_ai_text("HI!")

class SearchType4:
    def search(self, search_query):
        print("SearchType4 Activated!\n")
        self.update_ai_text("HI!")      