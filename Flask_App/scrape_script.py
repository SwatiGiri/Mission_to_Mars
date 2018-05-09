#
# The job of this script is to 
# scrape different websites and get data
# finally it pushes that data to mongo db
# Make sure to start your mongo db server before running
#
# Get functions are all helper functs
# scrape_and_push_to_db calls all the helper methods
#

print("Starting")
print("Importing Libraries")

from bs4 import BeautifulSoup as bs
import requests
import pymongo
from pymongo import MongoClient
from splinter import Browser
import pandas as pd
import time

# intializing mongo db
print("Initializing Mongodb...")
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars
collection = db.mars
print("Mongodb Initialized.")

def get_news():
    print("--------------------------------")
    print(" Getting News")
    print("--------------------------------")
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

    return  {
                "title" : news_title,
                "description" : news_p
            }

def get_featured_image():
    print("--------------------------------")
    print(" Getting Featured Image ")
    print("--------------------------------")
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
    return image_url

def get_weather():
    print("--------------------------------")
    print(" Getting Weather ")
    print("--------------------------------")
    # URL of page to be scraped
    url="https://twitter.com/marswxreport?lang=en"
    # Retrieve page with the requests module
    response= requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'lxml')
    # results 
    results = soup.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
    mars_weather = results[0].text

    return mars_weather

def get_facts():
    print("--------------------------------")
    print(" Getting Facts ")
    print("--------------------------------")

    url="https://space-facts.com/mars/"
    response= requests.get(url)
    soup = bs(response.text, 'lxml')
    # getting the table with all the facts
    results = soup.find('table', class_="tablepress tablepress-id-mars")
    # converting bs object to a string
    mars_info_table = str(results)
    # converting that html str to a df
    info_df = pd.read_html(mars_info_table)[0]
    # converting the df to html table (str)
    return info_df.to_html()

def get_hemisphere_images():    
    print("--------------------------------")
    print(" Getting Hemisphere Images")
    print("--------------------------------")

    BASE_ASTROLOGY_URL = "https://astrogeology.usgs.gov/"
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    response= requests.get(url)
    soup = bs(response.text, 'lxml')
    # Getting all the hemispheres urls, but the actual image is on another page

    image_page_urls = soup.find_all('a', class_="itemLink")
    images_data = []

    for image_page_url in image_page_urls:
        #  Getting a link to the other page, where we will then get the image
        url = BASE_ASTROLOGY_URL +  image_page_url["href"]
        # title we can extract right on this page
        title = image_page_url.find('h3').text
        response= requests.get(url)
        soup = bs(response.text, 'lxml')
        # getting the image url on the other page
        image_url = soup.find('a', {'target': '_blank'})['href'] 
        data = {'img_url' : image_url, 'title' : title}
        images_data.append(data)
        
    print(images_data)
    return images_data



# this is the absolute main func
# calls all of the other helper function 
# to get the information
# and then pushes that information to the db
def scrape_and_push_to_db():
    news = get_news()
    featured_img = get_featured_image()
    weather = get_weather()
    fact_as_html_table = get_facts()
    hemisphere_imgs = get_hemisphere_images()

    db.collection.insert_one({
        "news" : news,
        "featured_img" : featured_img,
        "weather" : weather,
        "facts" : fact_as_html_table,
        "hermisphere_imgs" : hemisphere_imgs
    })


if __name__ == "__main__":
    scrape_and_push_to_db()
