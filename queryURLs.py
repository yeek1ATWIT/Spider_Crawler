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

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        else:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            else:
                print(f"Failed to fetch {url} with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return None

def extract_names_and_nouns(text):
    blob = TextBlob(text)
    
    # Extract proper nouns (NNP) and nouns (NN, NNS)
    names = [word for word, pos in blob.tags if pos == 'NNP']
    nouns = [word for word, pos in blob.tags if pos in ['NN', 'NNS']]
    #print("Names:", names)
    #print()
    #print("Nouns:", nouns)

    return names, nouns

def filter_names(names, nouns):
    # Remove nouns from the names list
    filtered_names = [name for name in names if name.lower() not in [noun.lower() for noun in nouns]]
    return filtered_names

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
                "Information", "Property", "Listings"]

# Define regex patterns
name_regex = re.compile(
    r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    r'|\b[A-Z][a-z]+ [A-Z]\.? [A-Z][a-z]+\b'
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

# Checks if words in sub string is in main string
def contains_Credentials(main, sub):
    main_words = main.lower().split()
    sub_words = sub.lower().split()
    for word in sub_words:
        if word not in main_words:
            return False
    return True

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

def is_batch_credentials(text):
    dict_patterns = count_patterns(text)
    for key, value in dict_patterns.items():
        if (key == 'name' or key == 'address') and value <= 2:
            continue
        #if key == 'name' and dict_patterns['address'] > 0:
        #    continue
        if value > 1:
            return False
    return True

def count_list_entries_in_string(text, entries):
    # Convert text to lowercase for case insensitive matching
    text = text.lower()
    entries = [entry.lower() for entry in entries]
    
    # Tokenize the text into words
    words = text.split()
    total_words = len(words)
    
    # Count occurrences of list entries in the text
    entry_count = 0
    for word in words:
        if word in entries:
            entry_count += 1
    
    # Calculate the ratio of list entries to the total number of words
    ratio = entry_count / total_words if total_words > 0 else 0
    
    return total_words, ratio

# -1 = invalid, 0 = Undetermined, 1 = Valid
def isvalid(text):
    total_words, us_state_ratio = count_list_entries_in_string(text, state_names)
    total_words, letter_ratio = count_list_entries_in_string(text, alphabet_uppercase)
    if total_words > 20:
        #names, nouns = extract_names_and_nouns(text)
        #total_words, names_ratio = count_list_entries_in_string(text, names)
        #total_words, nouns_ratio = count_list_entries_in_string(text, nouns)

        names_nouns_ratio = 10
        #if nouns_ratio > 0:
        #    names_nouns_ratio = names_ratio/nouns_ratio

        if us_state_ratio > .3 or letter_ratio > .3 or names_nouns_ratio < 1:
            return -1
    else:
        if sum(count_patterns(text).values()) >= (total_words/3) and letter_ratio < .5:
            return 1
    return 0

def add_to_dict(nested_list, result_dict, indent=0):
    for item in nested_list:
        if isinstance(item, list):
            add_to_dict(item, result_dict, indent + 1)
        else:
            #value = isvalid(str(item))
            value = 0
            if value == -1:
                continue  # Skip this item and continue to the next one
            if value == 1 or value == 0:
                if is_batch_credentials(str(item)) and not any(entry.lower() in str(item).lower() for entry in header_names):
                    key = str(item).replace('\n', ' ')
                    #if key in result_dict:
                    #    count = result_dict[key][1] + 1
                    #else:
                    count = 1
                    result_dict[key] = (indent, count)
    return result_dict

def uniquify_dict(param_dict):
    unique_dict = {}
    
    keys = list(param_dict.keys())
    while keys:
        current_key = keys.pop(0)
        current_indent, current_count = param_dict[current_key]
        
        keys_to_remove = []
        for key in keys:
            indent, count = param_dict[key]
            if contains_Credentials(current_key, key):
                current_count += count
                keys_to_remove.append(key)
            elif contains_Credentials(key, current_key):
                current_key = key
                current_indent, current_count = param_dict[current_key]
                current_count += count
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            keys.remove(key)
        
        unique_dict[current_key] = (current_indent, current_count)
    
    return unique_dict

def sort_dict_by_count(param_dict):
    # Sort the dictionary by the count in the values (which is the second item in the tuple)
    sorted_dict = dict(sorted(param_dict.items(), key=lambda item: item[1][1], reverse=True))
    return sorted_dict

def find_split_index(nested_list, first_name, last_name, path=None):
    if path is None:
        path = []
        
    first_name_lower = first_name.lower()
    last_name_lower = last_name.lower()
    
    for i, item in enumerate(nested_list):
        current_path = path + [i]
        if isinstance(item, list):
            split_path = find_split_index(item, first_name, last_name, current_path)
            if split_path:
                return split_path
        elif isinstance(item, str):
            if first_name_lower in item.lower() or last_name_lower in item.lower():
                return current_path
    return None

def split_list_on_path(nested_list, path):
    def get_by_path(lst, path):
        for p in path:
            lst = lst[p]
        return lst
    
    def set_by_path(lst, path, value):
        for p in path[:-1]:
            lst = lst[p]
        lst[path[-1]] = value

    split_item = get_by_path(nested_list, path)
    
    # Split the item and update the original list
    first_half = split_item[:]
    second_half = split_item[:]
    
    # Clear the item at the split point in the original nested list
    set_by_path(nested_list, path, [])
    
    return nested_list, second_half

def split_list_on_name(nested_list, first_name, last_name):
    split_path = find_split_index(nested_list, first_name, last_name)
    if split_path is None:
        return nested_list, []
    
    return split_list_on_path(nested_list, split_path)

def extract_text_from_html(url):
    try:
        # Parse the HTML content
        soup = BeautifulSoup((fetch_response(url).text), 'html.parser')
    except:
        try:
            # Parse the HTML content
            soup = BeautifulSoup((fetch_response(url.replace("https://", "https://www.")).text), 'html.parser')    
        except:
            return []
    # Define a recursive function to extract text and nested tags
    def extract_text(tag):
        # Initialize an empty list to store the text and nested tags
        result = []
        
        # Extract text from the current tag
        text = tag.get_text(separator='\n').strip()
        if text:
            result.append(text)
        
        # Recursively process nested tags
        for child in tag.children:
            if child.name:
                result.append(extract_text(child))
        
        return result
    
    # Initialize an empty list to store the result
    text_list = []
    
    # Iterate over each top-level tag in the HTML content
    for tag in soup.find_all(['div', 'section', 'article', 'p', 'span']):
        # Extract text and nested tags recursively
        text_list.append(extract_text(tag))

    return text_list

def print_nested_list(nested_list, indent=0):
    for item in nested_list:
        if isinstance(item, list):
            print_nested_list(item, indent + 1)
        else:
            print("\t"*indent)
            print("\t"*indent+"ENTRY: "+str(item).replace('\n', ' '))

# Helper functions to check validation
def is_name(text):
    return bool(name_regex.fullmatch(text))

def is_address(text):
    return bool(address_regex.fullmatch(text))

def is_phone(text):
    return bool(phone_regex.fullmatch(text))

def is_age(text):
    return bool(age_regex.fullmatch(text))

# Function to combine dict keys based on the given rules
def combine_dict_elements(param_dict):
    keys = list(param_dict.keys())
    combined_dict = {}
    i = 0

    while i < len(keys):
        current_key = keys[i]
        current_indent, current_count = param_dict[current_key]

        # Check if the current key is a name and the next key is either an address, phone, or age
        if is_name(current_key) and \
           (i + 1 < len(keys) and (is_address(keys[i + 1]) or is_phone(keys[i + 1]) or is_age(keys[i + 1]))):

            combined_key = current_key
            combined_count = current_count

            j = i + 1
            while j < len(keys):
                next_key = keys[j]
                next_indent, next_count = param_dict[next_key]

                if is_address(next_key) or is_phone(next_key) or is_age(next_key):
                    combined_key += f"\n{next_key}"
                    combined_count += next_count
                    j += 1
                else:
                    break

            combined_dict[combined_key] = (current_indent, combined_count)
            i = j
        else:
            combined_dict[current_key] = (current_indent, current_count)
            i += 1

    return combined_dict

def contains_all_words(text1, text2):
    """Check if all words in text2 are present in text1."""
    words1 = set(text1.split())
    words2 = set(text2.split())
    return words2.issubset(words1)

def combine_dict_elements2(param_dict):
    keys = list(param_dict.keys())
    combined_dict = {}
    i = 0

    while i < len(keys):
        current_key = keys[i]
        current_indent, current_count = param_dict[current_key]

        if current_indent == 1:
            combined_key = current_key
            combined_count = current_count

            j = i + 1
            while j < len(keys):
                next_key = keys[j]
                next_indent, next_count = param_dict[next_key]
                
                if next_indent > 1:
                    if not contains_all_words(combined_key, next_key):
                        combined_key += f"\n{next_key}"
                        combined_count += next_count
                    j += 1
                else:
                    break

            combined_dict[combined_key] = (current_indent, combined_count)
            i = j
        else:
            combined_dict[current_key] = (current_indent, current_count)
            i += 1

    return combined_dict

def modify_dict_keys(param_dict):
    modified_dict = {}
    for key, value in param_dict.items():
        modified_key = key
        #counts = count_patterns(key)
        #if len([value for value in counts.values() if value > 0]) < 2:
        #    continue

        # Tokenize the text into words
        words = modified_key.split()
        total_words = len(words)
        if total_words <= 1:
            continue
        if value[1] <= 1:
            continue
        if "Alabama Alaska Arizona Arkansas".lower() in key.lower():
            continue
        if "A B C D E F G".lower() in key.lower():
            continue
        if "ANDORRA UNITED ARAB EMIRATES".lower() in key.lower():
            continue

        modified_dict[modified_key] = value

    return modified_dict

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

    phone_number = search_query.phone_number.value.replace(" ", "").replace("(", "").replace(")", "")

    fill_data = {
            'John': search_query.first_name.value,
            'Doe': search_query.last_name.value,
            '4321 Main St': search_query.street.value,
            '4321+Main+St': search_query.street.value.replace(' ','+'),
            'Dallas': search_query.city.value,
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

def get_results_from_url(url, search_query):
    result = extract_text_from_html(url)
    #result = split_list_on_name(result, search_query.first_name.value, search_query.last_name.value)
    moo = add_to_dict(result, {})
    #moo = combine_dict_elements(moo)
    moo = combine_dict_elements2(moo)
    moo = uniquify_dict(moo)
    moo = modify_dict_keys(moo)
    moo = sort_dict_by_count(moo)

    query_values = []
    query_values.append(search_query.first_name.value)
    query_values.append(search_query.last_name.value)
    #query_values = [getattr(search_query, attr).value for attr in search_query.__dict__]
    #query_values.pop(-1)
    #query_values.pop(-2)
    moo = {key: value for key, value in moo.items() if any(entry in key for entry in query_values)}


    #for key, value in moo.items():
    #    print("Entry: "+key+ " : "+str(value))

    return moo.keys()

def flatten_and_join(lst):
    result = ''
    for item in lst:
        if isinstance(item, list):
            result += flatten_and_join(item)
        else:
            result += str(item) + '\n'
    return result

def process_url(url, search_query):
    document = search.Document(url)
    document.url = fill_in_URL(url, search_query)
    info_list = get_results_from_url(document.url, search_query)
    document.info = flatten_and_join(info_list)
    
    info_words = document.info.split()
    if len(info_words) < 10:
        return None
    updateRelevance(search_query, document)
    document.info = highlight_names(document.info, search_query.first_name.value, search_query.last_name.value)
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



def highlight_names(text, first_name, last_name):
    # Create regex patterns
    combined_pattern = re.compile(rf'{first_name}\s+{last_name}', re.IGNORECASE)
    first_name_pattern = re.compile(rf'\b{first_name}\b', re.IGNORECASE)
    last_name_pattern = re.compile(rf'\b{last_name}\b', re.IGNORECASE)

    # Split the text into lines
    lines = text.split('\n')

    # Initialize lists to store the processed lines and the final matches
    processed_lines = []
    matches = []
    current_match = []

    # Iterate through the lines
    for line in lines:
        if combined_pattern.search(line):
            if current_match:
                matches.append('\n'.join(current_match))
                current_match = []
            current_match.append(line)
        elif first_name_pattern.search(line) or last_name_pattern.search(line):
            if current_match:
                matches.append('\n'.join(current_match))
                current_match = []
            current_match.append(line)
        else:
            current_match.append(line)
    
    if current_match:
        matches.append('\n'.join(current_match))

    matches.pop(0)
    matches.pop(0)

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
    search_query.first_name.value = search_query.first_name.value.capitalize()
    search_query.middle_name.value = search_query.middle_name.value.capitalize()
    search_query.last_name.value = search_query.last_name.value.capitalize()
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


"""