from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from scraper.scraperscripts.urls import urls

# from scraper.scraperscripts.myscript import get_reviews_from_url
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import json
import threading
import random

THREAD_COUNT = 5


async def index(request):
    myurls = urls["urls"]
    url_count = len(myurls) // THREAD_COUNT
    new_list = [myurls[i : i + url_count] for i in range(0, len(myurls), url_count)]
    print(new_list)

    # for url_list in new_list:
    #     t1 = threading.Thread(target=single_thread, args=(url_list,))
    #     t1.start()
    scrape_with_js(url=myurls[2])
    return HttpResponse("Hello, world !!!")


def scrape_with_js(url):
    driver = webdriver.Firefox()
    driver.implicitly_wait(60)
    driver.get(url)
    driver.execute_script(js_code)
    time.sleep(30)


def single_thread(url_list):
    driver = webdriver.Firefox()
    driver.implicitly_wait(60)
    for url in url_list:
        get_reviews_from_url(url, driver)


def get_inner_text(element, tag):
    try:
        soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")
        element = soup.find(tag)
        main_text = "".join(element.stripped_strings)
        return main_text
    except:
        return ""


def get_reviews_from_url(url, driver):
    print("opening url : ", url)
    reviews = []
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


js_code = """

console.log("Content script is running...");


const getReviews = async () => {
  let companyName = await getCompanyName();
  await clickReviewsButton();
  await wait(5000);
  await scrollToLastReview(20);
  let reviews = extractAllReviews();
  let data = { name: companyName, reviews: reviews };
  console.log(data);
  return data;
};

const extractAllReviews = () => {
  let allReviews = [];
  let allReviewsElements = document.getElementsByClassName("GHT2ce");
  for (i = 0; i < allReviewsElements.length; i++) {
    allReviewsElements[i].style.backgroundColor = "green";
    let review = extractReview(allReviewsElements[i]);
    let rating = extractRating(allReviewsElements[i]);
    if (rating > 0 || review !== "")
      [allReviews.push({ rating: rating, review: review })];
  }
  return allReviews;
};

const extractReview = (mainElement) => {
  let review = "";
  try {
    let reviewContainer = mainElement.getElementsByClassName("MyEned");
    let targetElement = reviewContainer[0].getElementsByClassName("wiI7pd");
    let thisReview = getInnerText(targetElement);
    console.log("review => ", thisReview);
    if (thisReview !== "") {
      review = thisReview;
    }
  } catch {}

  return review;
};
const extractRating = (mainElement) => {
  let ratingElements = mainElement.getElementsByClassName("DU9Pgb");
  let rating = 0;

  try {
    let ratingsContainer = ratingElements[0].getElementsByClassName("kvMYJc");
    let ratings = ratingsContainer[0].getElementsByTagName("img");
    for (i = 0; i <= ratings.length; i++) {
      if (
        ratings[i].src ===
        "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png"
      ) {
        rating = rating + 1;
      }
    }
  } catch {}

  console.log("rating => ", rating);
  return rating;
};

const scrollToLastReview = async (scrolls) => {
  return new Promise(async (resolve, reject) => {
    for (i = 0; i < scrolls; i++) {
      let reviewElements = document.getElementsByClassName("GHT2ce");
      let lastElement = reviewElements[reviewElements.length - 1];
      lastElement.scrollIntoView();
      await wait(5000);
    }
    resolve();
  });
};

const clickReviewsButton = async () => {
  let buttons = document.getElementsByClassName("hh2c6");
  return new Promise((resolve, reject) => {
    for (i = 0; i < buttons.length; i++) {
      for (const child of buttons[i].children) {
        let innerText = getInnerText(child);
        if (innerText === "Reviews") {
          child.click();
          resolve();
        } else {
          for (const chil of child.children) {
            let innerText = getInnerText(chil);
            if (innerText === "Reviews") {
              child.click();
              resolve();
            }
          }
        }
      }
    }
  });
};

const getCompanyName = async () => {
  return new Promise((resolve, reject) => {
    let companyNameElement = document.getElementsByTagName("h1");
    if (companyNameElement.length > 0) {
      for (i = 0; i < companyNameElement.length; i++) {
        let element = companyNameElement[i];
        let newname = getInnerText(element);

        if (newname !== "") {
          resolve(newname);
        }
      }
    }
  });
};

const getInnerText = (element) => {
  try {
    let consideredElement = element.length > 0 ? element[0] : element;
    consideredElement.style.backgroundColor = "red";
    var plainText =
      consideredElement.textContent || consideredElement.innerText;
    return plainText;
  } catch {
    return "";
  }
};

const wait = async (time) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve();
    }, time);
  });
};

getReviews();

"""
