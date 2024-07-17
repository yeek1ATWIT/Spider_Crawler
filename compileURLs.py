import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import requests
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
from textblob import TextBlob
from langdetect import detect
import re

def fetch_response(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return 

def fetch_html(url):
    return fetch_response(url).text

def extract_html_from_urls(file_path):
    urls_html = {}
    with open(file_path, 'r') as file:
        urls = [url.strip() for url in file.readlines()]

    for url in urls:
        html = fetch_html(url)
        if html:
            urls_html[url] = html

    return urls_html

def compare_html(html1, html2):
    sequence_matcher = difflib.SequenceMatcher(None, html1, html2)
    return sequence_matcher.ratio()

class URLFilter:
    def __init__(self, search_urls_file, banned_urls_file):
        self.search_urls_file = search_urls_file
        self.banned_urls_file = banned_urls_file

    def filter_urls(self):
        search_urls_html = extract_html_from_urls(self, self.search_urls_file)
        banned_urls_html = extract_html_from_urls(self, self.banned_urls_file)

        # Function to compare URL pairs
        def compare_urls(url1, html1, url2, html2):
            similarity = compare_html(html1, html2) 
            if similarity > 0.9:
                urls_to_move.add(url1)

        urls_to_move = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for search_url, search_html in search_urls_html.items():
                for banned_html in banned_urls_html.values():
                    executor.submit(compare_urls, search_url, search_html, None, banned_html)

        
        search_urls = list(search_urls_html.items())
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(len(search_urls)):
                url1, html1 = search_urls[i]
                for j in range(i + 1, len(search_urls)):
                    url2, html2 = search_urls[j]
                    executor.submit(compare_urls, url1, html1, url2, html2)

        
        urls_to_move = list(set(urls_to_move))

        if urls_to_move:
            self.update_files(urls_to_move)

    def update_files(self, urls_to_move):
        with open(self.search_urls_file, 'r') as file:
            urls = file.readlines()

        with open(self.search_urls_file, 'w') as file:
            for url in urls:
                if url.strip() not in urls_to_move:
                    file.write(url)

        with open(self.banned_urls_file, 'a') as file:
            for url in urls_to_move:
                file.write(url + '\n')

    

def read_file_to_set(filename):
    special_chars = ['ᵒ', '~', '^',  '*']

    if not os.path.exists(filename):
        return set()

    def remove_special_chars(line):
        special_chars_set = set(special_chars)
        index = len(line) - 1

        # Traverse the line from end to start
        while index >= 0 and line[index] in special_chars_set:
            index -= 1

        # Return the cleaned line up to the last non-special character
        return line[:index + 1]

    unique_items = set()
    with open(filename, 'r') as file:
        for line in file:
            cleaned_line = remove_special_chars(line.strip())
            unique_items.add(cleaned_line)
    
    return unique_items

def add_new_entries(filename, new_entries):
    unique_items = read_file_to_set(filename)
    new_unique_entries = set(new_entries) - unique_items

    if new_unique_entries:
        with open(filename, 'a') as file:
            for item in sorted(new_unique_entries):  # Sorting is optional
                file.write(f"{item}\n")
    return unique_items.union(new_unique_entries)

# True if no banned words in url html page
def check_banned_words_count(self, url_response):
        soup = BeautifulSoup(url_response.content, 'html.parser')
        text = soup.get_text()

        for word in self.banned_words:
            if text.lower().count(word.lower()) > 100:
                return False
        for word in self.sub_banned_words:
            if text.lower().count(word.lower()) > 20:
                return False
        for word in self.mini_banned_words:
            if text.lower().count(word.lower()) > 10:
                return False
        for word in self.mini_mini_banned_words:
            if text.lower().count(word.lower()) > 5:
                return False
            
        return True

# True if no banned words in url name
def check_banned_url_name(self, string):
        for word in self.sub_banned_words:
            if word in string.lower():
                return False
        for word in self.mini_banned_words:
            if word in string.lower():
                return False
        for word in self.mini_mini_banned_words:
            if word in string.lower():
                return False     
        return True

# True if approved words in url name
def check_approved_url_name(self, string):
    for word in self.approved_words:
        if word in string.lower():
            return True 
    return False

class Compiler:
    def __init__(self):
        self.inclusive_component_names = {
                'first_name': ['first_name', 'First-Name', 'firstname', 'First Name', 'First name', 'FirstName', 'first', 'First','firstName', 'FIRST NAME', 'name', 'Name', 'name-input'],
                'last_name': ['last_name', 'Last-Name', 'lastname', 'Last Name', 'Last name', 'LastName', 'last', 'Last', 'lastName', 'LAST NAME'],
                'address': ['address', 'Address', 'location-input'],
                'street' : ['street', 'Street'],
                'city': ['city', 'City', 'Town'],
                'state': ['state', 'State', 'Province'],
                'zipcode': ['zipcode', 'Zipcode', 'zip_code', 'Zip Code', 'Zip code', 'Postcode', 'Postal Code', 'PostalCode', 'Postalcode', 'postal_code'],
                'phone_number': ['phone_number', 'phone-number', 'PhoneNumber', 'phone', 'Phone', 'tel', 'Tel']
            }
        self.sample_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'address': '1234 Main St',
            'street': '1234 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zipcode': '12345',
            'phone_number': '123-456-7890'
        }
        self.submit_button_identifiers = ['SEARCH','button-search', 'perform-search', 'submit', 'enter', 'search', 'go', 'search now', 'submit now', 'proceed', 'confirm', 'next', 'submit form', 'submitBtn', 'flex']
        self.banned_words = ['home']
        self.sub_banned_words = ['job', 'company', 'firm', 'trail', 'walk', 'research']
        self.mini_banned_words = [ ' firm', 'contract', 'charity', 'news',  'celeb', 'license', 'nail', 'employee', 'customer']
        self.mini_mini_banned_words = ['tax', 'health', 'accounting', 'restaurant', 'estate', 'business', 'obituar', 'funeral', 'game', 'trademark']
        # Overrides banned words protocol
        self.approved_words = ['people', 'search', 'find']
        #self.new_compiled_urls = []
        self.driver = webdriver.Chrome()

        banned_urls_file = 'bannedSearchURLs.txt'
        self.banned_urls_html = extract_html_from_urls(banned_urls_file)

        submit_lower_len = len(self.submit_button_identifiers)
        for i in range(submit_lower_len):
            name = self.submit_button_identifiers[i]
            name = ' '.join(word.capitalize() for word in name.split())
            self.submit_button_identifiers.append(name)

    def is_on_banned_list(self, url_response):
        # Returns True if similar
        def compare_urls(url1, html1, url2, html2):
            return compare_html(html1, html2) > 0.9
            
        url_html = url_response.text

        if not url_html:
            return True
        
        with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_comparison = {executor.submit(compare_urls, url_response, url_html, None, banned_html): banned_html for banned_html in self.banned_urls_html.values()}
                for future in as_completed(future_to_comparison):
                    if future.result():
                        return True
        
        return False

    def compile(self, url, forwarding_list):
        #self.forward(url, forwarding_list)
        print(url)
        if not check_banned_url_name(self, url):
            print("Banned Name")
            return
        
        if "http" not in url:
            url = "https://"+url

        try:
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            valid_input_found = False
            for key, value in self.inclusive_component_names.items():
                for name in value:
                    try:
                        input_element = self.driver.find_element(By.XPATH, f"//a[contains(@name, '{name}')]")
                        input_element.send_keys(self.sample_data[key])
                        valid_input_found = True
                    except Exception:
                        pass
                    
                    try:
                        input_element = self.driver.find_element(By.XPATH, f"//a[contains(@aria-label, '{name}')]")
                        input_element.send_keys(self.sample_data[key])
                        valid_input_found = True
                    except Exception:
                        pass

                    try:
                        input_element = self.driver.find_element(By.XPATH, f"//a[contains(@id, '{name}')]")
                        input_element.send_keys(self.sample_data[key])
                        valid_input_found = True
                    except Exception:
                        pass
                    
                    try:
                        input_element = self.driver.find_element(By.XPATH, f"//input[contains(@title, '{name}')]")
                        input_element.send_keys(self.sample_data[key])
                        valid_input_found = True
                    except Exception:
                        pass

                    try:
                        input_element = self.driver.find_element(By.XPATH, f"//input[contains(@placeholder, '{name}')]")
                        input_element.send_keys(self.sample_data[key])
                        valid_input_found = True
                    except Exception:
                        pass

            if not valid_input_found:
                print("No Valid Input Found")
                return

            if not self.find_and_click_button():
                return
            
            # Wait for the next page to load and get the new URL
            time.sleep(2) 
            
            new_url = (self.driver.current_url).replace("www.", '')
            if new_url == url or new_url == url+'/':
                print("URL equals Original Page")
                return
            
            url_response = fetch_response(url)

            if not url_response:
                return
            
            if not check_banned_words_count(self, url_response) and not check_approved_url_name(self, url):
                print("Irrelevant Source")
                return

            if self.is_on_banned_list(url_response):
                print("On Sources Banned List")
                return

            #self.new_compiled_urls.append(url)
            print("PASSED: "+url+"\n")
            add_new_entries("searchURLs.txt", [url])

            # Wait for the next page to load and get the new URL
            time.sleep(2) 
        except:
           return

    def forward(self, url, forwarding_list):
        try:
            if "http" not in url:
                self.driver.get("https://"+url)
            else:
                self.driver.get(url)
        except:
            return
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        for name in self.inclusive_component_names:
            try:
                link = self.driver.find_element(By.XPATH, f"//a[contains(@name, '{name}')]")
                href = link.get_attribute('href')
                if href and href not in forwarding_list:
                    forwarding_list.append(href)
                    self.compile(href, forwarding_list)
                    return True
            except NoSuchElementException:
                pass

            try:
                link = self.driver.find_element(By.XPATH, f"//a[contains(@title, '{name}')]")
                href = link.get_attribute('href')
                if href and href not in forwarding_list:
                    forwarding_list.append(href)
                    self.compile(href, forwarding_list)
                    return True
            except NoSuchElementException:
                pass

            try:
                link = self.driver.find_element(By.XPATH, f"//a[contains(@placeholder, '{name}')]")
                href = link.get_attribute('href')
                if href and href not in forwarding_list:
                    forwarding_list.append(href)
                    self.compile(href, forwarding_list)
                    return True
            except NoSuchElementException:
                pass
        # Wait for the next page to load and get the new URL
            time.sleep(2) 
        return False

    def find_and_click_button(self):
        for identifier in self.submit_button_identifiers:
            try:
                button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{identifier}')]")
                button.click()
                return True
            except Exception:
                pass
            
            try:
                button = self.driver.find_element(By.XPATH, f"//button[contains(@id, '{identifier}') or contains(@type, '{identifier}') or contains(@aria-label, '{identifier}') or contains(@name, '{identifier}') or contains(@placeholder, '{identifier}')]")
                button.click()
                return True
            except Exception:
                pass
            
            try:
                button = self.driver.find_element(By.XPATH, f"//button[@type='submit'] | //div[@aria-label='Search'] | //input[@type='submit']")
                button.click()
                return True
            except Exception:
                pass
        print("No Valid Submit Found")
        return False
    
    def main(self):
        uncompiled_folder = 'uncompiledURLs'
        compiled_folder = 'compiledURLs'
        
        for filename in os.listdir(uncompiled_folder):
            file_path = os.path.join(uncompiled_folder, filename)
            urls = read_file_to_set(file_path)
            for url in urls:
                url = url.strip()
                if url:
                    self.compile(url, [])

            shutil.move(file_path, os.path.join(compiled_folder, filename))
            #add_new_entries("searchURLs.txt", self.new_compiled_urls)
            self.new_compiled_urls = []

search_urls_file = 'searchURLs.txt'
banned_urls_file = 'bannedSearchURLs.txt'

enable_ban_filter = False
if enable_ban_filter:
    url_filter = URLFilter(search_urls_file, banned_urls_file)
    url_filter.filter_urls()
else:
    compiler = Compiler()
    compiler.main()
