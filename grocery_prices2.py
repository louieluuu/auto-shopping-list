# -Retrieve price of certain items of interest (predetermined by list) from grocery wesbites: T&T, Superstore, Walmart.
#     -unclear if the URLs of items will stay the same over time, may have to use search function instead?
# -Checks if the prices fall below a certain threshold, again, predetermined by the user.    
    # -threshold prices should have two categories: max allowable price (still on sale), and cheapest - or near cheapest - seen prices.
    # -cheapest price (biggest, rarest sales) should be at the top of the Shopping List - could signify with (!)
# -If so, prints out item names and prices in readable list form, sorted by store. This is now the "Shopping List".
# -Somehow make the Shopping List accessible via mobile device (consider e-mail, perhaps an app?)

# -wondering if the app should have functionality: ex. the ability to change the threshold prices via phone.
# -accounts for drastic price shifts, ex. vegetable oil in 2022.

#for testing
from ast import Return
from cgitb import text
from tkinter import SCROLL
import unittest 

#for parsing robots.txt urls
#documentation here: https://docs.python.org/3.10/library/urllib.robotparser.html
import urllib.robotparser 
                          
#standard selenium imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#wait imports
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#to delay program execution with time.sleep(int)
import time
import random

#to export data as csv file
import pandas as pd

#setting path of webdriver (arbitrary)
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

#### setting up robot parser - unfortunately doesn't seem to work that well ####
# rp_url = "https://www.tntsupermarket.com/robots.txt"
# rp = urllib.robotparser.RobotFileParser(rp_url)
# rp.read()
# print(rp.can_fetch("*", "https://www.tntsupermarket.com/eng/75551501-tnt-thai-jasmine-rice-40lb.html"))

tnt_url = "https://www.tntsupermarket.com/eng/75551501-tnt-thai-jasmine-rice-40lb.html" # T&T is being weird, searching
# "t&t thai jasmine rice" won't return any results on the headless browser. additionally, visiting the link directly will 
# show a difference price ($43.xx) than the price on a normal browser ($46.19)




new_tab = "chrome://newtab"
superstore_url = "https://www.realcanadiansuperstore.ca/"

# instantiating Superstore items
class Item:
    def __init__(self, search, desired_item, max_buy_price, cheapest_price):
        self.search = search
        self.desired_item = desired_item
        self.max_buy_price = max_buy_price
        self.cheapest_price = cheapest_price

lentils = Item("red split lentils", "1.8 kg", 4.50, 3.99)
peas = Item("no name green peas", "Club Size", 5.00, 4.49)
oats = Item("quick oats", "5.16 kg", 10.00, 6.49)
peanut_butter = Item("no name peanut butter", "Club Size", 8.00, 6.99)
condensed_milk = Item("condensed milk", "Brand Sweetened Condensed Milk", 3.00, 2.49)
chicken_korma = Item("chicken korma", "President's Choice", 4.00, 3.49)
annies_crackers = Item("annies crackers", "White Cheddar", 4.00, 3.49)

superstore_items = [lentils, peas, oats, peanut_butter, condensed_milk, chicken_korma, annies_crackers]

# randomizing array to randomize search order (human behaviour)
random.shuffle(superstore_items)
    
# Stalls program execution by 3-7 seconds to simulate human web-scrolling behaviour.  
def stall():
    time.sleep(random.randint(3,7))

driver.implicitly_wait(5) # wait max 5 seconds before executing commands with the driver, replaces need for explicit waits (allegedly)
                          # note that if the command fails ex. element not found, error won't be thrown because there's no try... except structure

driver.get(new_tab)
driver.maximize_window() # human behaviour



######################### SUPERSTORE ################################

driver.get(superstore_url)
stall()

for i in range(len(superstore_items)):
    # close modals: not necessary for Superstore
    # close_modal_button = driver.find_element(By.ID, "closeActivityPop").click()

    # engage with search bar
    search = superstore_items[i].search
    search_bar = driver.find_element(By.CLASS_NAME, "search-input__input") 
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys(search)
    stall()
    search_bar.send_keys(Keys.RETURN)

    # find the div of the desired item from search results
    desired_item = superstore_items[i].desired_item
    search_results = driver.find_elements(By.TAG_NAME, "h3")

    for item in search_results:
        if desired_item in item.text:
            desired_item_div = item

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

        # compare the price to the max_buy_price
        if (price <= superstore_items[i].max_buy_price):
            print("{item} on sale! The price is: {price} vs the cheapest price: {cheapest_price}.".format(item = superstore_items[i].search.capitalize(), price = price, cheapest_price = superstore_items[i].cheapest_price))
        else:
            print("This item is not on sale: " + superstore_items[i].search)
            print("Moving on to the next item...")
            continue
    else:    
        print("This item is not on sale: " + superstore_items[i].search)
        print("Moving on to the next item...")
        continue

stall()


######################### NO FRILLS ################################

# instantiating No Frills items

lentils = Item("red split lentils", "1.8 kg", 4.50, 3.99)
peas = Item("no name green peas", "Club Size", 5.00, 4.49)
peanut_butter = Item("no name peanut butter", "Club Size", 7.99, 6.99)
condensed_milk = Item("condensed milk", "Brand Sweetened Condensed Milk", 3.00, 2.49)

nofrills_items = [lentils, peas, peanut_butter, condensed_milk]

# randomizing array to randomize search order (human behaviour)
random.shuffle(nofrills_items)

nofrills_url = "https://www.nofrills.ca/"
driver.get(nofrills_url)
stall()

for i in range(len(nofrills_items)):
    # close modals: not necessary for No Frills
    # close_modal_button = driver.find_element(By.ID, "closeActivityPop").click()

    # engage with search bar
    search = nofrills_items[i].search
    search_bar = driver.find_element(By.CLASS_NAME, "search-input__input") 
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys(search)
    stall()
    search_bar.send_keys(Keys.RETURN)

    # find the div of the desired item from search results
    desired_item = nofrills_items[i].desired_item
    search_results = driver.find_elements(By.TAG_NAME, "h3")

    for item in search_results:
        if desired_item in item.text:
            desired_item_div = item

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

        # compare the price to the max_buy_price
        if (price <= nofrills_items[i].max_buy_price):
            print("{item} on sale! The price is: {price} vs the cheapest price: {cheapest_price}.".format(item = nofrills_items[i].search.capitalize(), price = price, cheapest_price = nofrills_items[i].cheapest_price))
            continue
        else:
            pass
    print("This item is not on sale: " + nofrills_items[i].search)
    print("Moving on to the next item...")
    continue

stall()
driver.quit()
