import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup 
import pandas as pd
import time

# DB Setup

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

# Create Mission to Mars global dictionary that can be imported into Mongo
mars_info = {}

# NASA MARS NEWS
def scrape_mars_news():
    try: 

        # Initialize browser 
        browser = init_browser()

    # Nasa Mars news
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # HTML Object
    html = browser.html

   # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
     
   # Retrieve the latest element that contains news title and news_paragraph
    news_title = soup.find(class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text

   # Display scrapped data 
    print("This is the title:", news_title)
    print("Summary:", news_p)

    # JPL Mars Space Images - Featured Image
    url_image="https://www.jpl.nasa.gov/images/"
    base_url="https://www.jpl.nasa.gov"
    browser.visit(url_image)
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    soup.prettify()
    results2= soup.find_all('div', class_="SearchResultCard")
    first_results = results2[0]
    extend_url = first_results.find('a')["href"]
    img_url=base_url+extend_url
    print("featured_image_url:",img_url)

    # Mars fact
    # Visit Mars facts url 
    facts_url = 'http://space-facts.com/mars/'

    # Use Panda's `read_html` to parse the url
    mars_facts = pd.read_html(facts_url)


    # Find the mars facts DataFrame in the list of DataFrames as assign it to `mars_df`
    mars_df = mars_facts[0]

    # Save html code to folder Assets
    mars_df.to_html()

    # Display mars_df
    mars_df

    # Visit hemispheres website through splinter module 
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    # HTML Object
    html_hemispheres = browser.html

    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html_hemispheres, 'html.parser')

    # Retreive all items that contain mars hemispheres information
    items = soup.find_all('div', class_='item')

    # Create empty list for hemisphere urls 
    hemisphere_image_urls = []

    # Store the main_ul 
    hemispheres_main_url = 'https://astrogeology.usgs.gov'

    for i in items: 
    # Store title
        title = i.find('h3').text
    
    # Store link that leads to full image website
    partial_img_url = i.find('a', class_='itemLink product-item')['href']
    
    # Visit the link that contains the full image website 
    browser.visit(hemispheres_main_url + partial_img_url)
    
    # HTML Object of individual hemisphere information website 
    partial_img_html = browser.html
    
    # Parse HTML with Beautiful Soup for every individual hemisphere information website 
    soup = BeautifulSoup( partial_img_html, 'html.parser')
    
    # Retrieve full image source 
    img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
    
    # Append the retreived information into a list of dictionaries 
    hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
    

    # Display hemisphere_image_urls
    hemisphere_image_urls

    # Close the browser after scraping
    browser.quit()

    # Return results
    mars_data ={
		'news_title' : news_title,
		'news_p': news_p,
        'img_url': img_url,
		'mars_df' : mars_df,
		'hemisphere_image_urls': hemisphere_image_urls,
        'url': url,
        'url_image': url_image,
        'facts_url': facts_url,
        'hemispheres_main_url': hemispheres_main_url,
        }
    collection.insert(mars_data)