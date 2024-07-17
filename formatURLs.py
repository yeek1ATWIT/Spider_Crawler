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

def fetch_response(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return 

def add_url_to_file(filename, new_url):
    # Ensure the file exists
    if not os.path.exists(filename):
        open(filename, 'w').close()

    # Read the existing URLs from the file into a set
    with open(filename, 'r') as file:
        existing_urls = set(line.strip() for line in file)

    # Check for duplicates and add the new URL if it's not already present
    if new_url not in existing_urls:
        with open(filename, 'a') as file:
            file.write(f"{new_url}\n")
        print(f"Added URL: {new_url}")
    else:
        print(f"URL already exists: {new_url}")

def get_URLs_from_file(filename):
        if not os.path.exists(filename):
            print(f"{filename} does not exist.")
            return
        
        with open(filename, 'r') as file:
            urls = {line.strip() for line in file if line.strip()}
        return urls

class Formatter:
    def __init__(self):
        self.inclusive_component_names = {
                'first_name': ['first_name', 'First-Name', 'firstname', 'First Name', 'First name', 'FirstName', 'first', 'First','firstName', 'FIRST NAME'],
                'last_name': ['last_name', 'Last-Name', 'lastname', 'Last Name', 'Last name', 'LastName', 'last', 'Last', 'lastName', 'LAST NAME'],
                'name': ['name', 'Name', 'name-input'],
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
            'name': 'John Doe',
            'address': '4321 Main St',
            'street': '4321 Main St',
            'city': 'Dallas',
            'state': 'TX',
            'zipcode': '13579',
            'phone_number': '123-456-7890'
        }
        self.submit_button_identifiers = ['SEARCH','button-search', 'perform-search', 'submit', 'enter', 'search', 'go', 'search now', 'submit now', 'proceed', 'confirm', 'next', 'submit form', 'submitBtn', 'flex']
        self.driver = webdriver.Chrome()

    def compile(self, url, forwarding_list):
        #self.forward(url, forwarding_list)
        print(url)

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
                        if key == 'name' and valid_input_found:
                            break
                        # Combine all XPaths into a single XPath using the | operator
                        combined_xpath = (
                            f"//a[contains(@name, '{name}')] | "
                            f"//a[contains(@aria-label, '{name}')] | "
                            f"//a[contains(@id, '{name}')] | "
                            f"//input[contains(@title, '{name}')] | "
                            f"//input[contains(@placeholder, '{name}')]"
                        )
                        
                        input_element = self.driver.find_element(By.XPATH, combined_xpath)
                        if "John" in input_element.get_attribute("value") and key == 'last_name':
                            input_element.send_keys(" "+self.sample_data[key])
                            break
                        input_element.send_keys(self.sample_data[key])
                        valid_input_found = True
                        break
                            
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
            
            if all(value not in new_url for value in self.sample_data.values()):
                print("URL doesn't have any insertable credentials")
                return
            
            url_response = fetch_response(url)

            if not url_response:
                return

            #self.new_compiled_urls.append(url)
            print("PASSED: "+url+"\n")
            add_url_to_file("formattedSearchURLs.txt", new_url)

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
        search_urls_file = 'searchURLs.txt'
        urls = get_URLs_from_file(search_urls_file)

        for url in urls:
            self.compile(url, [])

formatter = Formatter()
formatter.main()