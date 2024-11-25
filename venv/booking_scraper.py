import concurrent.futures
import requests
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import re
import sys

def cleanText(text):
    text = text.strip()
    text = re.sub(r'\s{2,}', ' ', text)
    return text

def extract_numbers(input_string):
    pattern = r"[-+]?\d*\.\d+|\d+"
    numbers = re.findall(pattern, input_string)
    number = int(''.join(numbers))
    return number

def get_property_id(link):
    start_index = link.index("&all_sr_blocks=") + 15
    end_index = link.index("&highlighted_blocks=")
    range_value = link[start_index:end_index]
    hotel_id = range_value[:range_value.index("_") - 2]
    return hotel_id

data = {'Property Name': [],
        'Rating': [],
        'Review': [],
        'Price': [],
        'Tax': [],
        'Property Link': [],
        'Property Id': []
        }

url = sys.argv[1]
service = Service(executable_path='C:\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get(url)

search_text = "properties match your search but are outside"

try:
    pop_up = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "c000b8dd0b")))
    close_button = pop_up.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss sign-in info.']")
    close_button.click()
except:
    try:
        pop_up = driver.find_element(By.CLASS_NAME, "c000b8dd0b")
        close_button = pop_up.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss sign in information.']")
        close_button.click()
    except:
        pass

def scroll_to_bottom(driver_, search_text):
    while True:
        last_height = driver_.execute_script("return document.body.scrollHeight")
        driver_.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        
        if search_text in driver.page_source:
            break

        new_height = driver_.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

while True:
    try:
        scroll_to_bottom(driver, search_text)
        load_more = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.da4da790cd")))
        driver.execute_script("arguments[0].click();", load_more)
    except:
        break

properties = driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')
for index, property_ in enumerate(properties):
    try:
        property_name = property_.find_element(By.CLASS_NAME, "b121bc708f").text
    except:
        property_name = None
    print(index, "Property Name:", property_name)

    try:
        rating_element = property_.find_element(By.CLASS_NAME, "a438920765")
        rating_check = rating_element.find_element(By.TAG_NAME, "path").get_attribute("d")
        no_rating = "M112 8H16a8 8 0 0 0-8 8v96a8 8 0 0 0 8 8h96a8 8 0 0 0 8-8V16a8 8 0 0 0-8-8zM48 96H24V58h24zm56-25a8.7 8.7 0 0 1-2 6 8.9 8.9 0 0 1 1 4 6.9 6.9 0 0 1-5 7c-.5 4-4.8 8-9 8H56V58l10.3-23.3a5.4 5.4 0 0 1 10.1 2.7 10.3 10.3 0 0 1-.6 2.7L72 52h23c4.5 0 9 3.5 9 8a9.2 9.2 0 0 1-2 5.3 7.5 7.5 0 0 1 2 5.7z"
        if no_rating in rating_check:
            rating = float(0)
        else:
            rating = float(len(rating_element.find_elements(By.TAG_NAME, 'span')))
    except:
        rating = float(0)

    try:
        pre_review = property_.find_element(By.CLASS_NAME, "e008572b71").text
        in_review = property_.find_element(By.CLASS_NAME, "e008572b71").find_element(By.CLASS_NAME, "c617a39cca").text
        review = float(cleanText(pre_review.replace(in_review, "")))
    except:
        review = None

    try:
        price = float(extract_numbers(property_.find_element(
            By.CSS_SELECTOR, '[data-testid="price-and-discounted-price"]').text))
    except:
        price = float(0)

    try:
        tax = float((extract_numbers(property_.find_element(
            By.CSS_SELECTOR, '[data-testid="taxes-and-charges"]').text.replace("+", "").replace(" taxes and fees", ""))))
    except:
        tax = float(0)

    property_id_link = property_.find_element(By.CLASS_NAME, "eba3d3a8df").get_attribute("href")
    try:
        property_id = int(get_property_id(property_id_link))
    except:
        property_id = None

    data['Property Name'].append(property_name)
    data['Rating'].append(rating)
    data['Review'].append(review)
    data['Price'].append(price)
    data['Tax'].append(tax)
    data['Property Link'].append("")
    data['Property Id'].append(property_id)

df = pd.DataFrame(data)
driver.quit()
out = df.to_json(orient='records')[1:-1].replace('},{', '}~{')
#print(out)
