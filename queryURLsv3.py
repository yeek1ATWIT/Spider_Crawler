import os
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
#import nltk
import re
import search
import concurrent.futures
import database as db
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import time
import json
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

#nltk.download('punkt')
enable_robot_txt = False
enable_proxy_use = False
# Function to check url's robots.txt
def can_fetch(url, user_agent='*'):
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
    except:
        return False
    
    return rp.can_fetch(user_agent, url)

def fetch_with_playwright(url, timeout=1000):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout)
            response_body = page.content()
            browser.close()
            print(f"Playwright: Successfully loaded {url}")
            return response_body
    except PlaywrightTimeoutError:
        print(f"Playwright: Timeout error while loading {url}")
    except Exception as e:
        print(f"Playwright: An error occurred while loading {url}: {e}")
    return None

def fetch_with_selenium(url):
    try:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)

        options = Options()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  
        options.add_argument('--disable-gpu') 
        options.add_argument('--window-size=1920x1080') 
        options.add_argument('--no-sandbox') 
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        page = driver.page_source
        driver.quit()
        print(f"Selenium: Successfully loaded {url}")
        return page

    except Exception as e:
        print(f"Selenium: An error occurred while loading {url}: {e}")
    return None

proxies = [
    "38.154.227.167:5868:fqzoadia:tbr2g5705loa",
    "185.199.229.156:7492:fqzoadia:tbr2g5705loa",
    "185.199.228.220:7300:fqzoadia:tbr2g5705loa",
    "185.199.231.45:8382:fqzoadia:tbr2g5705loa",
    "188.74.210.207:6286:fqzoadia:tbr2g5705loa",
    "188.74.183.10:8279:fqzoadia:tbr2g5705loa",
    "188.74.210.21:6100:fqzoadia:tbr2g5705loa",
    "45.155.68.129:8133:fqzoadia:tbr2g5705loa",
    "154.95.36.199:6893:fqzoadia:tbr2g5705loa",
    "45.94.47.66:8110:fqzoadia:tbr2g5705loa"
]
def fetch_response(url):
    # Check if fetching the URL is allowed
    if enable_robot_txt and not can_fetch(url):
        print(f"Fetching {url} is disallowed by robots.txt")
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    if enable_proxy_use:
        for proxy_str in proxies:
            proxy = {
                'http': f'http://{proxy_str}',
                'https': f'https://{proxy_str}'
            }
            
            try:
                response = requests.get(url, headers=headers, proxies=proxy, timeout=5)
                if response.status_code == 200:
                    return response.text
                
                response = requests.get(url, proxies=proxy, timeout=5)
                if response.status_code == 200:
                    return response.text
            except requests.RequestException as e:
                hi = 1
                #print(f"Error fetching {url} with proxy {proxy_str}: {e}")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url} with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return None

###
state_abbreviations = {
    'alabama': 'AL',
    'alaska': 'AK',
    'arizona': 'AZ',
    'arkansas': 'AR',
    'california': 'CA',
    'colorado': 'CO',
    'connecticut': 'CT',
    'delaware': 'DE',
    'florida': 'FL',
    'georgia': 'GA',
    'hawaii': 'HI',
    'idaho': 'ID',
    'illinois': 'IL',
    'indiana': 'IN',
    'iowa': 'IA',
    'kansas': 'KS',
    'kentucky': 'KY',
    'louisiana': 'LA',
    'maine': 'ME',
    'maryland': 'MD',
    'massachusetts': 'MA',
    'michigan': 'MI',
    'minnesota': 'MN',
    'mississippi': 'MS',
    'missouri': 'MO',
    'montana': 'MT',
    'nebraska': 'NE',
    'nevada': 'NV',
    'new hampshire': 'NH',
    'new jersey': 'NJ',
    'new mexico': 'NM',
    'new york': 'NY',
    'north carolina': 'NC',
    'north dakota': 'ND',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'rhode island': 'RI',
    'south carolina': 'SC',
    'south dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'vermont': 'VT',
    'virginia': 'VA',
    'washington': 'WA',
    'west virginia': 'WV',
    'wisconsin': 'WI',
    'wyoming': 'WY'
}

state_names = ["New", "West", "DC", "Rhode" "Alabama", "North", "South", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
                   "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
                   "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
                   "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "Hampshire",
                   "Jersey", "Mexico", "York", "Carolina", "Dakota", "Ohio", "Oklahoma",
                   "Oregon", "Pennsylvania", "Island", "Carolina", "Dakota", "Tennessee",
                   "Texas", "Utah", "Vermont", "Virginia", "Washington", "Washington", "Virginia",
                   "Wisconsin", "Wyoming"]
alphabet_uppercase = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
header_names = ["Phone", "Number", "Relative", "Residence", "Address", "Name", "Length", "Lives"
                "Email", "Location", "People", "Background", "Previous", "Select", "Known", "Lived", "Browse",
                "Median", "Filter", "Under", "Value", "AK AL AR AZ CA CO CT DE DC", "Records", "Contact", "Site",
                "Privacy", "Conditions", "Directory", "Testimonials", "Profile", "Search", "$", "Living", "Details",
                "Login", "Register", "Registry", "About", "Terms", "Professional", "Company", "Skills", "Help",
                "Information", "Property", "Listings", "adsbygoogle", "Criminal", "Bankruptcy", "Death", "Report",
                "Source", "Incorporation", "Sort", "Relevance"]

# Define regex patterns
name_regex = re.compile(
    r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+ [A-Z]\.? [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+  [A-Z][a-z]+  [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+  [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+  [A-Z]\.?  [A-Z][a-z]+\b'
)
address_regex = re.compile(
    r'(?:(?:[A-Z][a-z]+(?: [A-Z][a-z]+)*, )?[A-Z][a-z]+(?: [A-Z][a-z]+)*), [A-Z]{2} \d{5}(?:-\d{4})?'  
    r'|(?:\d+\s+[A-Za-z]+\s+[A-Za-z]+(?:\s+[A-Za-z]+)*,?\s*[A-Za-z]+,?\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?)'
    r'|(\d+\s+[A-Z]?[a-zA-Z]+\s+[A-Z]?[a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*,\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*,\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?)' 
    r'|(\d+\s+[A-Za-z]+\s+[A-Za-z]+,\s+[A-Za-z]+,\s+[A-Z]{2}\s+\d{5})' 
)
phone_regex = re.compile(
    r'(?:(?:\(\d{3}\) ?|\d{3}-)\d{3}-\d{4}|\+\d{1,2} \d{3} \d{3} \d{4})'
    r'|[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
)
age_regex = re.compile(
    r'Age (\d{1,2}|\(\d{1,2}\))'
    r'|\(\d{1,2}\)'
)

patterns = {
        'address': address_regex,
        'age': age_regex,
        'name': name_regex,
        'phone': phone_regex
    }

# Function to count occurrences of each regex pattern in a string without overlapping
def count_patterns(text):
    counts = {key: 0 for key in patterns}
    used_indices = set()
    text.replace("*",'1')
    text.replace("xxxx",'1111')
    text.replace("xxx",'111')
    for key, pattern in patterns.items():
        for match in pattern.finditer(text):
            if not any(i in used_indices for i in range(match.start(), match.end())):
                counts[key] += 1
                used_indices.update(range(match.start(), match.end()))
    return counts

def phone_format(phone_number):
    clean_phone_number = re.sub('[^0-9]+', '', phone_number)
    formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1-", "%d" % int(clean_phone_number[:-1])) + clean_phone_number[-1]
    formatted_phone_number = "({}) {}-{}".format(*formatted_phone_number.split("-"))
    return formatted_phone_number

def get_queries(search_query):
    queries = []
    if search_query.first_name.value:
        queries.append(search_query.first_name.value)

    if search_query.last_name.value:
        queries.append(search_query.last_name.value)

    phone_number = search_query.phone_number.value.replace(" ", "").replace("(", "").replace(")", "")
    if phone_number:
        queries.append(phone_format(phone_number))
    
    if search_query.street.value:
        queries.append(search_query.phone.value)

    if search_query.city.value:
        queries.append(search_query.city.value)
    
    if search_query.state.value:
        queries.append(search_query.state.value)

    if search_query.zipcode.value:
        queries.append(search_query.zipcode.value)
    
    if len(queries) == 0:
        return "9032u32ionds", "0932h 98ms2ois"
    
    if len(queries) == 1:
        return queries[0], queries[0]
    
    return queries[0], queries[1]

def extract_text_from_html2(url, search_query):
    query1, query2 = get_queries(search_query)
    try:
        soup = BeautifulSoup(fetch_response(url), 'html.parser')
    except:
        try:
            soup = BeautifulSoup(fetch_response(url.replace("https://", "https://www.")), 'html.parser')
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
    for tag in soup.find_all(['div', 'section', 'article', 'p', 'span']):
        text_list.extend(extract_text(tag))

    flat_list = flatten_list(text_list)
    
    combined_entries = []
    current_entry = []
    consecutive_names = False

    for i, entry in enumerate(flat_list):
        word_count = len(entry.split())
        patterns_count = count_patterns(entry)
        contains_name = patterns_count['name'] > 0
        contains_address = patterns_count['address'] > 0

        if any(header.lower() in entry.lower() for header in header_names):
            continue
        if patterns_count['address'] > 1:
            continue
        if patterns_count['phone'] > 1:
            continue
        if patterns_count['age'] > 0 and contains_name:
            continue
        if (word_count > 14 or patterns_count['age'] > 0) and contains_address:
            continue
        if word_count > 5 and not contains_address:
            continue

        if contains_name:
            consecutive_names = True

            # Look ahead to the next entry to check if it is also a name
            if i + 1 < len(flat_list):
                next_entry = flat_list[i + 1]
                next_patterns_count = count_patterns(next_entry)
                next_contains_name = next_patterns_count['name'] > 0
                if not next_contains_name:
                    consecutive_names = False

            if consecutive_names:
                current_entry.append(entry)
            else:
                if current_entry:
                    combined_entry = '\n'.join(dict.fromkeys(current_entry))
                    if query1.lower() in combined_entry.lower() or query2.lower() in combined_entry.lower(): 
                        combined_entries.append(combined_entry)
                current_entry = [entry]
                
        else:
            current_entry.append(entry)

    if current_entry:
        combined_entry = '\n'.join(dict.fromkeys(current_entry))
        if query1.lower() in combined_entry.lower() or query2.lower() in combined_entry.lower():
            combined_entries.append(combined_entry)
    
    # Remove duplicate combined entries
    unique_combined_entries = list(dict.fromkeys(combined_entries))

    unique_combined_entries_length = len(unique_combined_entries)
    banned_index = []
    result = []
    for i in range(unique_combined_entries_length-1):
        for j in range(i+1, unique_combined_entries_length):
            if ' '.join(unique_combined_entries[i].lower().split()) in ' '.join(unique_combined_entries[j].lower().split()) or ' '.join(unique_combined_entries[j].lower().split()) in ' '.join(unique_combined_entries[i].lower().split()):
                if i not in banned_index and j not in banned_index:
                    banned_index.append(j)

    for i in range(unique_combined_entries_length):
        if i not in banned_index:
            result.append(unique_combined_entries[i])

    if len(result) > 0:
        if isheader(result[0]):
            result.remove(result[0])

    return result

def contains(small, big):
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return True
    return False

def isheader(text):
    try:
        words = text.split()
        if contains(["Virginia", "Wisconsin", "Wyoming",], words):
            return True
        if contains(["Candidates", "and", "Political",], words):
            return True
        if contains(["Centeda"], words):
            return True
        if contains(["HOME", "Offenders", "blog"], words):
            return True
        if contains(["Age", "Range", "to", "Age"], words):
            return True
        if contains(["Toggle", "navigation", "city,", "state,"], words):
            return True
        return False
    except:
        return False

def print_nested_list(nested_list, indent=0):
    for item in nested_list:
        if isinstance(item, list):
            print_nested_list(item, indent + 1)
        else:
            print("\t"*indent)
            print("\t"*indent+"ENTRY: "+str(item).replace('\n', ' '))

def get_URLs_from_file(filename):
        if not os.path.exists(filename):
            print(f"{filename} does not exist.")
            return
        
        with open(filename, 'r') as file:
            urls = {line.strip() for line in file if line.strip()}
        return urls

def fill_in_URL(url, search_query):
    search_query_state = 'ALL'
    if search_query.state.value:
        if search_query.state.value.lower() in state_abbreviations or search_query.state.value.upper() in state_abbreviations:
            search_query_state = state_abbreviations[search_query.state.value.lower()]
    
    search_query_city = 'ALL'
    if search_query.city.value:
        search_query_city = search_query.city.value

    phone_number = search_query.phone_number.value.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")

    fill_data = {
            'John': search_query.first_name.value,
            'Doe': search_query.last_name.value,
            '4321 Main St': search_query.street.value,
            '4321+Main+St': search_query.street.value.replace(' ','+'),
            'Dallas': search_query_city,
            'TX': search_query_state,
            'Texas': search_query_state,
            '13579': search_query.zipcode.value,
            '123-456-7890': '-'.join([phone_number[:3], phone_number[3:6], phone_number[6:]]),
            '1234567890': phone_number,
            '(123)456-7890': f'({phone_number[:3]}){phone_number[3:6]}-{phone_number[6:]}'
        }
    for key, value in fill_data.items():
        url = re.sub(re.escape(key), value, url, flags=re.IGNORECASE)
    return url

def process_url(url, search_query):
    document = search.Document(url)
    document.url = fill_in_URL(url, search_query)
    document.info = highlight_names2(extract_text_from_html2(document.url, search_query))
    update_relevance_score(search_query, document)
    if document.info:
        db.save_document_to_db(document)
    return document

def update_relevance_score(search_query, document, picture_in_document=False):
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

def highlight_names2(matches):
    if not matches:
        return None
    # Create the HTML content with bordered boxes for each match
    html_content = '<table>'
    for i in range(0, len(matches), 2):
        row = '<tr>'
        row += '<td style="border: 1px solid black; padding: 10px;">' + matches[i].replace("\n", "<br>") + '</td>'
        if i + 1 < len(matches):
            row += '<td style="border: 1px solid black; padding: 10px;">' + matches[i + 1].replace("\n", "<br>") + '</td>'
        row += '</tr>'
        html_content += row
    html_content += '</table>'

    return html_content

def capitalize_name(search_query):
    search_query.first_name.value = search_query.first_name.value.lower().capitalize()
    search_query.middle_name.value = search_query.middle_name.value.lower().capitalize()
    search_query.last_name.value = search_query.last_name.value.lower().capitalize()
    return search_query

##################
def extract_paragraphs(url):
    html_content = fetch_response(url)
    if html_content is None:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all(['p', 'yt-formatted-string'])
    relevant_paragraphs = [p.get_text() for p in paragraphs if p.get_text().strip()]

    return '<br>'.join(relevant_paragraphs[:3]) # Returns first 3 Para

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

def parse_engine_url(url):
    exclude_list = [
            "startpage",
            "system1",
            "bing",
            "StartpageSearch",
            "infospace.com"
        ]
    try:
        soup = BeautifulSoup(fetch_response(url), 'html.parser')
    except:
        try:
            soup = BeautifulSoup(fetch_response(url.replace("https://", "https://www.")), 'html.parser')
        except:
            return []
    links = soup.find_all('a', attrs={'href': True})
    urls = []
    for link in links:
        href = link.get('href')
        if href:
            if not any(exclude in href for exclude in exclude_list):
                urls.append(href)
    return urls

def process_engine_result(engine_result_url, search_query):
    document = search.Document(engine_result_url)
    document.info = extract_paragraphs(engine_result_url)
    if document.info:
        update_relevance_score(search_query, document)
        if document.relevance_score > 0:
            db.save_document_to_db(document)

def fetch_and_process_engine(engine_url, search_query):
    engine_result_urls = list(set(parse_engine_url(engine_url)))
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_engine_result, url, search_query) for url in engine_result_urls]
        concurrent.futures.wait(futures)

def get_unified_input(search_query):
    inputs = []
    query_values = search_query.get_all_entries_except_picture()
    for i in range(len(query_values)):
        if query_values[i].value is not None:
            inputs.append(query_values[i].value)
    return ' '.join(inputs) 

###############
def process_output_picture_url(driver):
    result = []
    links = driver.find_elements(By.XPATH, '//a[@class="richImgLnk"]')
    for link in links:
        
        data_m = link.get_attribute('data-m')

        if not data_m:
            continue

        data = json.loads(data_m)
        murl = data.get('murl')
        purl = data.get('purl')
        turl = data.get('turl')
        # This link is likely just the image on the website
        if murl:
            None 
            #print("Zelda:")
            #print(f"murl: {murl}")

        # This link is likely the website with the image
        if purl:
            result.append(purl) 
            #print("Zelda:")
            #print(f"purl: {purl}")

        # This link is likely just the image on the engine
        if turl:
            None 
            #print("Zelda:")
            #print(f"turl: {turl}")

    links = driver.find_elements(By.XPATH, '//a[@class="truncate" or contains(@class, "CbirSites-ItemDomain") or contains(@class, "GZrdsf")]')
    for link in links:
        href = link.get_attribute('href')
        if not href:
            continue

        result.append(href)
        #print("Zelda:")
        #print(href)

    return result[:5]

def process_input_picture_url(driver, temp_file):
    xpath_elements = [ 
    '//*[@id="upload-button"]'
    ]
    camera_icon = None
    try: 
        camera_icon = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, ' | '.join(xpath_elements)))
        )
    except:
        print("")
    try:
        if not camera_icon:
            xpath_elements = [
            '//*[@id="sbi_b"]',  
            '//*[@class="Gdd5U"]', 
            "//button[contains(@class, 'input__button')]"
            ]

            camera_icon = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, ' | '.join(xpath_elements)))
            )
            camera_icon.click()
    except:
        return False
    try:
        xpath_elements = [
        '//*[@id="sb_fileinput"]',  
        '//*[@id="upload_box"]',
        "//input[@type='file']" 
        ]
        file_input = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, ' | '.join(xpath_elements)))
        )
        file_input.send_keys(temp_file.name)
    except:
        return False
    return True
    
def parse_picture_url(driver, url, temp_file):
    driver.get(url)
    driver.get(url)
    if process_input_picture_url(driver, temp_file):
        time.sleep(4) 
        return process_output_picture_url(driver)
    return []

def parse_picture_urls(search_query, urls):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_file.write(search_query.picture.value)
    temp_file.close()

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)

    options = Options()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    options.add_argument('--disable-gpu') 
    options.add_argument('--window-size=1920x1080') 
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    results = []
    for url in urls:
        try:
            results.extend(parse_picture_url(driver, url, temp_file))
        except:
            print("Failed to parse link: "+url)
    driver.quit()
    os.remove(temp_file.name)
    return results

# Function to run parse_picture_urls in multiple threads
def parse_picture_urls_threads(search_query, all_urls, batch_size=2):
    results = []
    num_batches = math.ceil(len(all_urls) / batch_size)
    url_batches = [all_urls[i*batch_size:(i+1)*batch_size] for i in range(num_batches)]

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_batch = {executor.submit(parse_picture_urls, search_query, batch): batch for batch in url_batches}

        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                result = future.result()
                results.extend(result)
            except Exception as exc:
                print(f'Batch {batch} generated an exception: {exc}')
            else:
                print(f'Batch {batch} parsed successfully')

    return results

def process_picture_result(picture_result_url, search_query):
    document = search.Document(picture_result_url)
    document.info = extract_paragraphs(picture_result_url)
    if document.info is None:
        return
    update_relevance_score(search_query, document, True)
    db.save_document_to_db(document)

def parse_picture(search_query):
    if not search_query.picture.value:
        return
    urls = [
        'https://www.bing.com/images',
        'https://tineye.com/',
        'https://images.google.com/',
        'https://yandex.com/images/'
    ]
    result_urls = parse_picture_urls_threads(search_query, urls, 1)
    for result_url in result_urls:
        process_picture_result(result_url, search_query)

def parse_scrapers(search_query):
    documents = []
    filename = 'formattedSearchURLs.txt'
    urls = get_URLs_from_file(filename)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_url, url, search_query) for url in urls]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                document = future.result()
                if document:
                    documents.append(document)
            except Exception as exc:
                print(f'Generated an exception: {exc}')

def parse_engine(search_query):
    query = get_unified_input(search_query)

    engine_urls = [
            search_bing(query, 1),
            #search_dogpile(query, 1),
            #search_duckduckgo(query, 1),
            search_startpage(query, 1),
            search_bing(query, 2),
            #search_duckduckgo(query, 2),
            search_startpage(query, 2),
            #search_bing(query, 3),
            #search_duckduckgo(query, 3),
            #search_startpage(query, 3)
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_and_process_engine, url, search_query) for url in engine_urls]
        concurrent.futures.wait(futures)
    

def query(search_query):
    search_query = capitalize_name(search_query)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(parse_picture, search_query),
            executor.submit(parse_scrapers, search_query),
            #executor.submit(parse_engine, search_query)
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f'Generated an exception: {exc}')
