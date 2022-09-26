# for testing
from ast import Return
from asyncio.windows_events import NULL
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
database = client.open("Grocery Database")
superstore_worksheet = database.worksheet("Superstore")
database_range = "A2:G"
nofrills_worksheet = database.worksheet("No Frills")

# setting up webdriver
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.implicitly_wait(5) # if element is not found on the page due to loading, 
                          # driver will wait until element has loaded, up to a max of 5 secs

new_tab = "chrome://newtab"
superstore_url = "https://www.realcanadiansuperstore.ca/"
shopping_list = []

# Step 1: Import the Grocery Database from Google Sheets into a CSV list, superstore_items.
# each item in superstore_items contains the following values:
# item[0] = item_url
# item[1] = item
# item[2] = search
# item[3] = search_filter
# item[4] = regular_price
# item[5] = max_buy_price
# item[6] = cheapest_price

######################### SUPERSTORE ################################

superstore_items = superstore_worksheet.get_values(database_range)
random.shuffle(superstore_items) # human behaviour: randomize search order

driver.get(new_tab)
driver.maximize_window() # human behaviour
driver.get(superstore_url)
stall()

for item in superstore_items:
    # close modals:
    #

    # define variables, as specified in Step 1
    item_url = item[0]
    search = item[2]
    search_filter = item[3]
    regular_price = item[4]
    max_buy_price = float(item[5])
    cheapest_price = float(item[6])

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
        if search_filter in result.text:
            filtered_item_div = result
            print("Filtered_item_div found!: " + result.text)
            break
        else:
            filtered_item_div = ""
            print("Filtered_item_div NOT found!")
    
    if (not filtered_item_div):
        print("{Item} not found in the search results. Moving on to the next item...".format(Item = search.upper()))
        stall()
        continue  

   # if the item_url wasn't inputted, set it (may be useful to user, but annoying for the user to input themselves)
    if (not item_url):
        url = filtered_item_div.find_element(By.TAG_NAME, "a").get_attribute("href")

        # update the database
        item_cell = superstore_worksheet.find(search)
        url_cell = "A" + str(item_cell.row)
        superstore_worksheet.update(url_cell, url)

        # update the item
        item[0] = url

    badge_div = filtered_item_div.find_element(By.XPATH, "./following-sibling::div/div[1]") # redundant/out of place
    # if the item is not on sale, update the regular price weekly
    if (not badge_div.text):
        regular_price_div = filtered_item_div.find_element(By.XPATH, "./following-sibling::div")
        regular_price = regular_price_div.find_element(By.CSS_SELECTOR, ".price__value.selling-price-list__item__price.selling-price-list__item__price--now-price__value")
        regular_price = float((regular_price.text.replace("$", "")))

        # update the database
        item_cell = superstore_worksheet.find(search)
        regular_price_cell = "E" + str(item_cell.row)
        superstore_worksheet.update(regular_price_cell, regular_price)

        # update the item
        item[4] = regular_price

    # check if the desired item is on sale 
    # note: we assume a Superstore item is on sale IFF its badge div contains text
    price_div = filtered_item_div.find_element(By.XPATH, "./following-sibling::div/div[2]")
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
            print("{item} is on sale! Adding to the Shopping List...".format(item = search.capitalize()))
            item.append(price) # saving the price so we can access it later as current_price

            # if the cheapest price wasn't inputted, OR price is the cheapest yet seen...
            if (not cheapest_price or price < cheapest_price):
                # update the database
                item_cell = superstore_worksheet.find(search)
                cheapest_price_cell = "G" + str(item_cell.row)
                superstore_worksheet.update(cheapest_price_cell, price)
                # update the item
                item[6] = price
            shopping_list.append(item)
            continue
        else:
            pass

    print("This item is not on sale: " + search + ". Moving on to the next item...")

# SHOPPING LIST LOGIC #
try: 
    shopping_sheet = client.open("Shopping List (Louie)").sheet1
    shopping_sheet.clear()
except gspread.exceptions.SpreadsheetNotFound:
    shopping_sheet = client.create("Shopping List (Louie)")
    shopping_sheet.share("goldjet32@gmail.com", perm_type="user", role="writer")
    shopping_sheet = client.open("Shopping List (Louie)").sheet1

shopping_titles = "A1:E1"
shopping_sheet.update(shopping_titles, [["URL", "Item", "Regular Price", "Current Price", "Cheapest Price"]])

# each item in superstore_items contains the following values:
# item[0] = URL
# item[1] = item
# item[2] = search
# item[3] = search_filter
# item[4] = regular_price
# item[5] = max_buy_price
# item[6] = cheapest_price
# item[7] = current_price (appended earlier)

# append the sale items
for item in shopping_list:
    url = item[0]
    item_name = item[1]
    regular_price = item[4]
    current_price = item[7]
    cheapest_price = item[6]
    new_row = [url, item_name, regular_price, current_price, cheapest_price]
    shopping_sheet.append_row(new_row)

# format the spreadsheet
shopping_sheet.columns_auto_resize(1, 4) # exclude the URL to keep it small
shopping_sheet.format([shopping_titles], {"textFormat": {"fontSize": 10, "bold": True}})

driver.quit()
quit()












######################### NO FRILLS ################################

nofrills_items = database.worksheet("No Frills").get_values("B2:E")
random.shuffle(nofrills_items)

nofrills_url = "https://www.nofrills.ca/"
driver.get(nofrills_url)
stall()

for item in nofrills_items:
    # close modals:
    #

    # define variables, as specified in Step 1
    search = item[0]
    desired_item = item[1]
    max_buy_price = float(item[2])
    cheapest_price = float(item[3])

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
        stall()
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
            # print("{item} on sale! The price is: {price} vs the cheapest price: {cheapest_price}.".format(item = search.capitalize(), price = price, cheapest_price = cheapest_price))
            print("{item} is on sale! Adding to the Shopping List...".format(item = search.capitalize()))
            continue
        else:
            pass
    print("This item is not on sale: " + search + ". Moving on to the next item...")

driver.quit()

