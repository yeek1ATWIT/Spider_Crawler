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
import search
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import database as db

nltk.download('punkt')

def fetch_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    headers3 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        response = requests.get(url, headers=headers2)
        if response.status_code == 200:
            return response
        response = requests.get(url, headers=headers3)
        if response.status_code == 200:
            return response
        response = requests.get(url)
        if response.status_code == 200:
            return response
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
        soup = BeautifulSoup(fetch_response(url).text, 'html.parser')
    except:
        try:
            soup = BeautifulSoup(fetch_response(url.replace("https://", "https://www.")).text, 'html.parser')
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
    return result


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

    phone_number = search_query.phone_number.value.replace(" ", "").replace("(", "").replace(")", "")

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
    updateRelevance(search_query, document)
    if document.info:
        db.save_document_to_db(document)
    return document

def updateRelevance(search_query, document):
    info_words = document.info.split()
    search_query_attr = search_query.get_all_entries()
    search_query_attr.pop(-1)  # Remove the last element

    # Initialize weights
    weights = [False, False, False, False, False]

    # Map index ranges to weight indices
    weight_indices = [
        (range(3), 0),  # First three attributes
        (range(3, 4), 1),  # Fourth attribute
        (range(4, 5), 2),  # Fifth attribute
        (range(5, 8), 3),  # Sixth to eighth attributes
        (range(8, 9), 4)  # Ninth attribute
    ]

    # Update weights based on the presence of words in info
    for word in info_words:
        for i, attr in enumerate(search_query_attr):
            if word.lower() in attr.value.lower():
                for index_range, weight_index in weight_indices:
                    if i in index_range:
                        weights[weight_index] = True

    # Calculate relevance score
    document.relevance_score = 0
    weight_indices_to_attr = [0, 3, 4, 5, 8]
    for weight, attr_index in zip(weights, weight_indices_to_attr):
        if weight:
            document.relevance_score += search_query_attr[attr_index].weight

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

def query(search_query):
    search_query = capitalize_name(search_query)
    documents = []
    filename = 'formattedSearchURLs.txt'
    urls = get_URLs_from_file(filename)

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks to the executor
        futures = [executor.submit(process_url, url, search_query) for url in urls]
        
        # Collect the results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                document = future.result()
                if document:
                    documents.append(document)
            except Exception as exc:
                print(f'Generated an exception: {exc}')

    return documents
"""    
response = "https://publicrecordsnow.com/name/Johnny+Depp/Miami/FL/"
#response = "https://www.privateeye.com/people/Daniel+Miles/-none-/?_csrf=dkrqypnupn"
#response = "https://cityzor.com/M/Miles/Daniel/"
#response = "https://kwold.com/profile/search?fname=John&lname=Doe&state=KS&city=&fage="
#response = "https://realpeoplesearch.com/name/john-doe"
#response = "https://www.advanced-people-search.com/people/John+Doe/Dallas/TX/"
#response = "https://backgroundcheck.run/ng/profile/search?fname=John&lname=Doe&state=TX&city=Dallas"

result = extract_text_from_html(response)
moo = add_to_dict(result, {})
#moo = combine_dict_elements(moo)
moo = combine_dict_elements2(moo)
moo = uniquify_dict(moo)
moo = modify_dict_keys(moo)
moo = sort_dict_by_count(moo)



url = "https://www.anywho.com/people/Johnny+Depp/+ALL/"
url = "https://www.privateeye.com/people/Johnny+Depp//?_csrf=eljjuojcsk"
ls = extract_text_from_html2(url, "Johnny", "Depp")
for en in ls:
    print("["+en+"]")
"""