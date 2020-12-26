from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from bs4 import BeautifulSoup
from multiprocessing.pool import Pool
from multiprocessing import current_process
from functools import partial
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import re
import itertools
import time
import csv
import concurrent.futures

# Main Functions


def get_cat(full_url):
    # Input: Page with cltohing types
    # Output: List of URLs of all types

    # Selenium driver
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'
    path = '/Users/ericmestiza/Documents/Projects/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument(f'user-agent={user_agent}')
    options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.get(full_url)

    elems = driver.find_elements_by_class_name("card__link-full")
    cat_list = [elem.get_attribute('href') for elem in elems]

    driver.quit()

    return cat_list


cat_list = get_cat('https://www.patagonia.com/shop/womens')

cat_list.pop(0)
cat_list

cat_dict = {}


def cat_itemize(cat_url):
    # Input: URL of each category
    # Output: List of URLs of all items in each category

    global cat_dict

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'
    path = '/Users/ericmestiza/Documents/Projects/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument(f'user-agent={user_agent}')
    options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.get(cat_url)

    # Name of the category
    cat_name = driver.find_element_by_xpath(
        '/html/body/main/section/div[3]/div[1]/div/div[1]/div/div[1]/div').text

    if cat_name not in cat_dict:
        driver.get(cat_url)
        # If more than one page, click "LOAD MORE"
        while True:
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#product-search-results > div:nth-child(2) > div > div > div.row.product-grid.load-more-present > div.col-12.grid-footer > div.show-more.is-desktop-only > div > button")))
                button = driver.find_element_by_css_selector(
                    "#product-search-results > div:nth-child(2) > div > div > div.row.product-grid.load-more-present > div.col-12.grid-footer > div.show-more.is-desktop-only > div > button")
                button.location_once_scrolled_into_view
                button.click()
                time.sleep(5)
            except NoSuchElementException:
                break
            except TimeoutException:
                break

        all_items = driver.find_element_by_xpath(
            "//*[@id='product-search-results']/div[2]/div/div/div[2]")
        items = all_items.find_elements_by_class_name("product-tile")
        cat_items = [item.get_attribute(
            'data-monetate-producturl') for item in items]

        cat_dict[cat_name] = cat_items
        driver.quit()

    return cat_dict


with open('patagonia_items.json', 'a') as bm:
    bm.write(json.dumps(cat_dict))

for i in range(len(cat_list)):
    cat_itemize(cat_list[i])

with open('patagonia_items.json') as d:
    cat_dict_load = json.loads("[" +
                               d.read().replace("}{", "},\n{") +
                               "]")

a = list(cat_dict_load[1].values())

a[0][0]

patag_url_list = []
for i in range(len(cat_dict_load)):
    l = list(cat_dict_load[i].values())
    for j in range(len(l[0])):
        patag_url_list.append(l[0][j])
len(patag_url_list)

patag_url = patag_url_list[0]
patag_url

url_list = []


def patag_scraper(patag_url_list, url_list):

    # Input: URL from Patagonia
    # Output: DF with results

    # Define empty lists to store results and log of failed URLs
    failed = []
    results = []

    for patag_url in tqdm(patag_url_list):
        if patag_url not in url_list:
            # Empty dictionary to store output
            patag_results = {}

            # Beautiful soup driver
            HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4238.2  Safari/537.36',
            }
            content = requests.get(patag_url, headers=HEADERS)
            soup = BeautifulSoup(content.text, 'html.parser')

            # Selenium driver
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4238.2  Safari/537.36'
            path = '/Users/ericmestiza/Documents/Projects/chromedriver'
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument(f'user-agent={user_agent}')
            options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
            driver = webdriver.Chrome(executable_path=path, options=options)
            driver.get(patag_url)

            # Check if product is in stock
            try:
                #                 outofstock = driver.find_element_by_xpath('//*[@id="oos-label"]/h3').text
                #                 if NoSuchElementException:
                #                     pass
                #                 if outofstock=='OUT OF STOCK':
                #                     failed.append(patag_url)
                #                     pass

                #                 else:
                # Name of product
                patag_name = soup.find(
                    'div', {"class": "hero-pdp__intro-content"}).h1.get_text()
                patag_results['Name'] = patag_name

                # Material of product
                # *Click "Specs & Features" button*
                button = driver.find_element_by_xpath(
                    "/html/body/main/section/div[4]/section/div[2]/div/div/div/div/a")
                button.click()
                patag_mat = [el.text for el in driver.find_elements_by_xpath(
                    "/html/body/main/section/div[4]/section/div[4]/div/div/div/ul")]
                patag_results['Material'] = patag_mat

                # Color of product
                patag_color = []
                for color in soup.find('div', {"class": "row swiper-wrapper"}).find_all('h3', {'class': 'product-tile__name'}):
                    patag_color.append(color.get_text())
                patag_results['Color'] = patag_color

                # URL of product
                patag_results['URL'] = patag_url

                # Image tag of product
                patag_image = []
                for img in soup.find('div', {"class": "row swiper-wrapper"}).find_all('div', {'data-image-zoom-url': True}):
                    patag_image.append(img['data-image-zoom-url'])
                patag_results['Image'] = patag_image

                # Dict of Color : Image URL
                clr_img_dict = {}
                for color in patag_color:
                    for img in patag_image:
                        clr_img_dict[color] = img
                patag_results['Color:Image'] = clr_img_dict

                # Description of product
                patag_description = [desc.text for desc in driver.find_elements_by_xpath(
                    "/html/body/main/section/div[4]/section/div[3]/div/div/div/ul")]
                patag_results['Description'] = patag_description

                # Add dict output to list
                results.append(patag_results)

            except (NoSuchElementException, AttributeError):
                if NoSuchElementException:
                    failed.append(patag_url)
                elif AttributeError:
                    failed.append(patag_url)
                pass

            if len(results) > 0:
                f = open("patag_table.csv", "a")
                writer = csv.DictWriter(
                    f, fieldnames=['Name', 'Material', 'Color', 'URL', 'Image', 'Color:Image', 'Description'])
                writer.writeheader()
                writer.writerows(results)
                f.close()
                results = []
            if len(failed) > 0:
                with open("failed_patag.txt", 'a') as ft:
                    for row in failed:
                        ft.write(str(row) + '\n')
                failed = []


# Scraper
patag_urls = patag_url_list[156:]
print(len(patag_urls), patag_urls[0])

patag_url_list[570]

patag_scraper(patag_url_list[571:], url_list)

failed = open('failed_patag.txt', 'r').readlines()
len(failed)

f = list(set(failed))
len(f)

patag_df = pd.read_csv('patag_table.csv')
patag_df

patag_df = patag_df.drop_duplicates()
patag_df.index = range(len(patag_df))
patag_df.to_csv('patag_table.csv', index=False)

url_list = [i for i in patag_df['URL']] + f
len(url_list)


def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))


t = Diff(patag_url_list, url_list)
len(t)

patag_scraper(res, url_list)

res = list(filter(None, t))
len(res)
