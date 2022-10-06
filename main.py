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
from selenium.common.exceptions import NoSuchElementException

# for delaying program execution
from time import sleep
import random

# for reading and writing Google Sheets
import gspread # a separate library whose purpose is to facilitate using Google Sheets' API 
from oauth2client.service_account import ServiceAccountCredentials

# for handling data
import pandas as pd

# importing stores
# from stores import Superstore

# human behaviour: stall program execution to simulate web-surfing  
def stall():
    sleep(random.randint(3,7))

# connecting to Google API. The variable "client" will be used to interact with Google Sheets.
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)
database = client.open("Grocery Database")
store = database.worksheet("Superstore")
database_range = "A2:G"

# setting up webdriver
PATH = "D:\Programming\Projects\selenium-groceries\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.implicitly_wait(5) # if element is not found on the page due to loading, 
                          # driver will wait until element has loaded, up to a max of 5 secs

new_tab = "chrome://newtab"
shopping_list = []

# Step 1: Import the Grocery Database from Google Sheets into a CSV list, superstore_items.
# each item in superstore_items contains the following values:
# item[0] = item_url
# item[1] = item_name
# item[2] = search
# item[3] = search_filter
# item[4] = regular_price
# item[5] = max_buy_price
# item[6] = cheapest_price

class Superstore():
    url = "https://www.realcanadiansuperstore.ca/"
    def search_bar():
        search_bar = driver.find_element(By.CLASS_NAME, "search-input__input")
        return search_bar

    def search_results():
        search_results = driver.find_elements(By.CLASS_NAME, "product-tile__details__info")
        return search_results

    def badge():
        badge = filtered_item.find_element(By.CSS_SELECTOR, ".product-badge__icon.product-badge__icon--limit.product-badge__icon--product-tile")
        return badge

    def sale_price():
        try:    
            sale_price = filtered_item.find_element(By.CSS_SELECTOR, ".product-badge__text.product-badge__text--product-tile").text
        except NoSuchElementException:
            sale_price = ""
        return sale_price

    def regular_price():
        regular_price = filtered_item.find_element(By.CSS_SELECTOR, ".selling-price-list.selling-price-list--product-tile").text
        return regular_price




######################### SUPERSTORE ################################

global filtered_item
filtered_item = None

items = store.get_values(database_range)
random.shuffle(items) # human behaviour: randomize search order

driver.get(new_tab)
driver.maximize_window() # human behaviour
driver.get(Superstore.url)
stall()

for item in items:
    # close modals:
    #

    # define variables, as specified in Step 1
    item_url = item[0]
    item_name = item[1]
    search = item[2]
    search_filter = item[3]
    regular_price = item[4]
    max_buy_price = float(item[5])
    
    # this try except block is necessary to cover the case where
    # all initial cheapest_price fields are set to nothing.
    try:
        cheapest_price = item[6]
    except IndexError:
        item.append("")
        cheapest_price = ""

    # Step 1: Engage with search bar
    search_bar = Superstore.search_bar()
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys(search)
    stall()
    search_bar.send_keys(Keys.RETURN)

    # Step 2: Filter desired item from search results
    # combing through too many search results may match an unrelated item that happens to share the search_filter.
    # therefore, introduce a search cap.
    search_results = Superstore.search_results()
    search_cap = 8
    i = 0
    while i < min(len(search_results), search_cap):
        if search_filter in search_results[i].text: 
            filtered_item = search_results[i]
            break
        else:
            i += 1

    if (filtered_item == None):
        print(f"{search.upper()} not found in the search results. Moving on to the next item...")
        stall()
        continue

    # Step 3: Determine if the filtered item is on sale.
    price = Superstore.sale_price()
    if ("LIMIT" in price):
        # ex. format: $4.29 LIMIT 4
        price_array = price.split()
        price = float(price_array[0].replace("$", ""))

    elif ("FOR" in price):
        # ex. format: 2 FOR $9.00
        price_array = price.split()
        divisor = float(price_array[0])
        price = float(price_array[2].replace("$", ""))
        price = float(f"{(price/divisor):.2f}")

    elif (price == ""): # item is not on sale: update the regular price
        regular_price = Superstore.regular_price()
        # ex. formats: $6.69ea, $11.49c01
        regular_price = regular_price.replace("$", "")
        regular_price = float(regular_price[0:regular_price.index(".")+3])

        # update the database
        item_cell = store.find(search)
        regular_price_cell = "E" + str(item_cell.row)
        store.update(regular_price_cell, regular_price)

        # update the item
        item[4] = regular_price

        print(f"{search.upper()} is not on sale. Moving on to the next item...")
        continue
        
    # Step 4: Compare the price to the max_buy_price.
    if (price <= max_buy_price):
        print(f"{search.upper()} is on sale! Adding to the Shopping List...")
        item.append(price) # saving the price so we can access it later as current_price

        # if the cheapest price wasn't inputted, OR price is the cheapest yet seen...
        if (cheapest_price == "" or price < cheapest_price):
            # update the database
            item_cell = store.find(search)
            cheapest_price_cell = "G" + str(item_cell.row)
            store.update(cheapest_price_cell, price)
            # update the item
            item[6] = price

        shopping_list.append(item)

    elif (price > max_buy_price):
        print(f"{search.upper()} is on sale, but still too expensive to buy. Moving on to the next item...")
        continue

    stall()
    # reset filtered_item
    filtered_item = None 

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

# each item contains the following values:
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

