from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import json
import threading
import random


def get_inner_text(element, tag):
    try:
        soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")
        element = soup.find(tag)
        main_text = "".join(element.stripped_strings)
        return main_text
    except:
        return ""


url = "https://www.google.com/maps/search/web+dev+bangalore/@12.9767427,77.5117375,12z?entry=ttu"

# create a new Firefox session
driver = webdriver.Firefox()
driver.implicitly_wait(60)
driver.get(url)
time.sleep(30)


soup_level1 = BeautifulSoup(driver.page_source, "lxml")

reviews = []
urls = []

for link in soup_level1.find_all("a", class_="hfpxzc"):
    urls.append(link.attrs["href"])

print(urls)
print(len(urls), " companies...")
print("Waiting for all companies to be in the DOM.")
print("Scroll till the end...")
time.sleep(30)

chunked_urls = [urls[i : i + 20] for i in range(0, len(urls), 20)]
print(chunked_urls)
print("Writing json...")
file_path = str(random.randint(100000, 999999)) + "urls.json"
with open(file_path, "w") as json_file:
    json.dump({"urls": urls}, json_file, indent=4)


def get_reviews_from_url(url, driver):
    print("opening url : ", url)
    driver.get(url)
    time.sleep(30)
    try:
        company_name_element = driver.find_element(By.TAG_NAME, "h1")
        company_name = get_inner_text(company_name_element, "h1")
    except:
        company_name = "No Name..."

    print("Finding reviews for ", company_name)

    buttons = driver.find_elements(By.CLASS_NAME, "hh2c6")
    reviews_button = None
    for button in buttons:
        for child in button.find_elements(By.TAG_NAME, "div"):
            if child.get_attribute("innerHTML").strip() == "Reviews":
                reviews_button = button
                break
        if reviews_button:
            break
    if reviews_button:
        reviews_button.click()
        time.sleep(10)
        try:
            js_code = "arguments[0].scrollIntoView();"
            for i in range(20):
                print("scrolling--- ", i)
                ght2ce_elements = driver.find_elements(By.CLASS_NAME, "GHT2ce")
                last_element = ght2ce_elements[-1]
                driver.execute_script(js_code, last_element)
                time.sleep(5)
        except:
            pass

        company_reviews = []
        ght2ce_elements = driver.find_elements(By.CLASS_NAME, "GHT2ce")
        print("found ", len(ght2ce_elements), " reviews. :)")

        for element in ght2ce_elements:
            company_rating = 0
            for child in element.find_elements(By.CLASS_NAME, "DU9Pgb"):
                try:
                    ratings_container = child.find_element(By.CLASS_NAME, "kvMYJc")
                    ratings = ratings_container.find_elements(By.TAG_NAME, "img")
                    company_rating = len(ratings)
                except:
                    pass
            print("rating: ", company_rating)
            for child in element.find_elements(By.CLASS_NAME, "MyEned"):
                try:
                    review = get_inner_text(child, "div")
                    print("review: ", review)
                    company_reviews.append({"rating": company_rating, "review": review})
                except Exception as e:
                    print(e)
        reviews.append({"name": company_name, "reviews": company_reviews})

    driver.close()
    print("Writing json...")
    print(reviews)
    file_path = str(random.randint(100000, 999999)) + ".json"
    with open(file_path, "w") as json_file:
        json.dump({"all": reviews}, json_file, indent=4)


def single_thread(urls):
    for url in urls:
        get_reviews_from_url(url)


# for url_list in urls:
#     t1 = threading.Thread(target=single_thread, args=(url_list,))
#     t1.start()
