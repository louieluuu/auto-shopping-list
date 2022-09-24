# for testing
from ast import Return
from cgitb import text
from tkinter import SCROLL
import unittest 

# for parsing robots.txt urls
# documentation here: https://docs.python.org/3.10/library/urllib.robotparser.html
import urllib.robotparser 

#### testing the robot parser - unfortunately doesn't seem to work that well on Superstore & No Frills ####
# rp_url = "https://www.tntsupermarket.com/robots.txt"
# rp = urllib.robotparser.RobotFileParser(rp_url)
# rp.read()
# print(rp.can_fetch("*", "https://www.tntsupermarket.com/eng/75551501-tnt-thai-jasmine-rice-40lb.html"))
                          
# standard selenium imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# for delaying program execution
from time import sleep
import random

# for reading and writing Google Sheets
import gspread # a separate library whose purpose is to facilitate using Google Sheets' API 
from oauth2client.service_account import ServiceAccountCredentials

# for handling data
import pandas as pd

# human behaviour: stall program execution to simulate web-surfing  
def stall():
    sleep(random.randint(3,7))

# connecting to Google API. The variable "client" will be used to interact with Google Sheets.
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)

# setting up webdriver
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.implicitly_wait(5) # if element is not found on the page due to loading, 
                          # driver will wait until element has loaded, up to a max of 5 secs

new_tab = "chrome://newtab"
superstore_url = "https://www.realcanadiansuperstore.ca/"

# Step 1: Import the Grocery Database from Google Sheets into a CSV list, superstore_items.
# each element in superstore_items contains the following values:
# element[0] = search
# element[1] = desired_item
# element[2] = max_buy_price
# element[3] = cheapest_price

sheet = client.open("Grocery Database")
superstore_items = sheet.worksheet("Superstore").get_values("B2:E")
random.shuffle(superstore_items) # human behaviour: randomize search order

driver.get(new_tab)
driver.maximize_window() # human behaviour

######################### SUPERSTORE ################################

driver.get(superstore_url)
stall()

for i in range(len(superstore_items)):
    # close modals:
    #

    # define variables, as specified in Step 1
    search = superstore_items[i][0]
    desired_item = superstore_items[i][1]
    max_buy_price = float(superstore_items[i][2])
    cheapest_price = float(superstore_items[i][3])

    # engage with search bar
    search_bar = driver.find_element(By.CLASS_NAME, "search-input__input") 
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys(search)
    stall()
    search_bar.send_keys(Keys.RETURN)

    # find the div of the desired item from search results
    search_results = driver.find_elements(By.TAG_NAME, "h3")

    for result in search_results:
        if desired_item in result.text:
            desired_item_div = result
            break
        else:
            desired_item_div = None
    
    if desired_item_div == None:
        print("{Item} not found in the search results. Moving on to the next item...".format(Item = search.upper()))
        continue  

    # check if the desired item is on sale 
    # note: we assume a Superstore item is on sale IFF its badge div contains text
    badge_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[1]")
    price_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[2]")
    if (badge_div.text): # IFF
        # get the price
        if ("LIMIT" in badge_div.text): # limit format: "$4.29 LIMIT 4"
            price_array = price_div.text.split()
            price = price_array[0]
            price = float((price.replace("$", "")))
        elif ("MULTI" in badge_div.text): # multi format: "2 FOR $7.00"
            price_array = price_div.text.split()
            price = price_array[2]
            price = price.replace("$", "")
            price = float ( format( ( float(price)/float(price_array[0]) ), ".2f" ) ) # formatting necessary due to price sometimes being 1 decimal place

        stall()

        # compare the price to the max_buy_price
        if (price <= max_buy_price):
            print("{item} on sale! The price is: {price} vs the cheapest price: {cheapest_price}.".format(item = search.capitalize(), price = price, cheapest_price = cheapest_price))
            continue
        else:
            pass
    print("This item is not on sale: " + search + ". Moving on to the next item...")

######################### NO FRILLS ################################

nofrills_items = sheet.worksheet("No Frills").get_values("B2:E")
random.shuffle(nofrills_items)

nofrills_url = "https://www.nofrills.ca/"
driver.get(nofrills_url)
stall()

for i in range(len(nofrills_items)):
    # close modals:
    #

    # define variables, as specified in Step 1
    search = nofrills_items[i][0]
    desired_item = nofrills_items[i][1]
    max_buy_price = float(nofrills_items[i][2])
    cheapest_price = float(nofrills_items[i][3])

    # engage with search bar
    search_bar = driver.find_element(By.CLASS_NAME, "search-input__input") 
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys(search)
    stall()
    search_bar.send_keys(Keys.RETURN)

    # find the div of the desired item from search results
    search_results = driver.find_elements(By.TAG_NAME, "h3")

    for result in search_results:
        if desired_item in result.text:
            desired_item_div = result
            break
        else:
            desired_item_div = None
    
    if desired_item_div == None:
        print("{Item} not found in the search results. Moving on to the next item...".format(Item = search.upper()))
        continue  

    # check if the desired item is on sale 
    # note: we assume a No Frills item is on sale IFF its badge div contains text
    badge_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[1]")
    price_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[2]")
    sale_price_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[3]")

    if (badge_div.text): # IFF
        # get the price
        if ("LIMIT" in badge_div.text): # limit format: "$4.29 LIMIT 4"
            price_array = price_div.text.split()
            price = price_array[0]
            price = float((price.replace("$", "")))
        elif ("MULTI" in badge_div.text): # multi format: "$4.50 MIN 2"
            price_array = price_div.text.split()
            price = price_array[0]
            price = float( price.replace("$", "").format(".2f") ) # formatting necessary due to price sometimes being 1 decimal place
        elif ("SALE" in badge_div.text): # sale format: "$4.29ea$5.99ea $0.24/ 100g"
            price_array = sale_price_div.text.split("ea")
            price = price_array[0]
            price = float(price.replace("$", ""))

        stall()

        # compare the price to the max_buy_price
        if (price <= max_buy_price):
            print("{item} on sale! The price is: {price} vs the cheapest price: {cheapest_price}.".format(item = search.capitalize(), price = price, cheapest_price = cheapest_price))
            continue
        else:
            pass
    print("This item is not on sale: " + search + ". Moving on to the next item...")

driver.quit()
