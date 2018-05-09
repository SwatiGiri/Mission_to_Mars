from bs4 import BeautifulSoup as bs
import requests
import pymongo
from pymongo import MongoClient
from splinter import Browser
import time

# intializing mongo db
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars
collection = db.mars

# getting news from 
# and saving to mongo db
# object look like for querying "news" : { "title", "description" }
def get_news():
    # URL of page to be scraped
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latesthttps://mars.nasa.gov/news/"
    # Retrieve page with the requests module
    response= requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'lxml')
    # results are returned as an iterable list
    results = soup.find_all('div', class_="slide")


    news_title = ""
    news_p = ""
    for result in results:
        # Error handling
        try:
            # Identify and return title of listing
            title = result.find('div', class_='content_title').find('a').text
            # Identify and return price of listing
            paragraph = result.find('div', class_="rollover_description_inner").text
            # Print results only if title, price, and link are available
            if (title and paragraph):
                print('-------------')
                print(title)
                print(paragraph)
                news_title, news_p = title ,paragraph
            # since we only need the first news, we will break right after we find it
            # comment line below to get all the news
            break
            
        except AttributeError as e:
            print(e)
    # -- for loop end -- 
    news_p = news_p.strip()
    news_title = news_title.strip()

    # adding data to mongo db
    return { "news" : {
                "title" : news_title,
                "description" : news_p
            }
        }

def get_featured_image():
    # opening browser using splinter
    executable_path = {'executable_path': 'C:/Users/swati/Downloads/chromedriver_win32/chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    # URL of page to be scraped
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    # opening the website
    browser.visit(url)
    # clicking on link to enlarge the image 
    browser.find_by_css('.fancybox').first.click()

    # stop for a bit so the click changes can be persisted
    # if you remove this there is a possibility that 
    # you will get html before click makes any changes
    time.sleep(3)

    # getting the html for the website
    html=browser.html
    soup = bs(html, 'lxml')
    soup.prettify()
    # find information for featured image 
    results = soup.find('img', class_="fancybox-image")
    print(results)
    # extracting the url 
    image_url = "https://www.jpl.nasa.gov" + results['src']
    print(image_url)
    browser.quit()
    # pushing url to mongo db
    return { "featured_image" : image_url}

# def 


def scrape_and_push_to_db():
    news = get_news()
    featured_img = get_featured_image()
    db.collection.insert_one({
        news,
        featured_img
    })


if __name__ == "__main__":
    scrape_and_push_to_db()