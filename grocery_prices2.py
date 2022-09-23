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


# instantiating Superstore foods
class Food:
    def __init__(self, search, desired_item, max_buy_price, cheapest_price):
        self.search = search
        self.desired_item = desired_item
        self.max_buy_price = max_buy_price
        self.cheapest_price = cheapest_price

lentils = Food("red split lentils", "1.8 kg", 4.49, 3.99)
peas = Food("no name green peas", "Club Size", 4.99, 4.49)
oats = Food("quick oats", "5.16 kg", 8.99, 6.49)
peanut_butter = Food("no name peanut butter", "Club Size", 7.99, 6.99)
condensed_milk = Food("condensed milk", "Brand Sweetened Condensed Milk", 2.99, 2.49)

superstore_foods = [lentils, peas, oats, peanut_butter, condensed_milk]

# randomizing array to randomize search order (human behaviour)
superstore_foods_randomized = []
for i in range(len(superstore_foods)):
    rand_i = random.randint(0, len(superstore_foods)-1)
    superstore_foods_randomized.append(superstore_foods[rand_i])
    superstore_foods.pop(rand_i)



    
# Stalls program execution by 3-7 seconds to simulate human web-scrolling behaviour.  
def stall():
    time.sleep(random.randint(3,7))

driver.implicitly_wait(5) # wait max 5 seconds before executing commands with the driver, replaces need for explicit waits (allegedly)
                          # note that if the command fails ex. element not found, error won't be thrown because there's no try... except structure

driver.get(new_tab)
driver.maximize_window() # human behaviour

driver.get(superstore_url)
stall()

    # close modals: not necessary for Superstore
    # close_modal_button = driver.find_element(By.ID, "closeActivityPop").click()

for i in range(len(superstore_foods_randomized)):
    # engage with search bar
    search = superstore_foods_randomized[i].search

    search_bar = driver.find_element(By.CLASS_NAME, "search-input__input") 
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys(search)
    stall()
    search_bar.send_keys(Keys.RETURN)

    # find the div of the desired item from search results
    desired_item = superstore_foods_randomized[i].desired_item
    
    search_results = driver.find_elements(By.TAG_NAME, "h3")

    for item in search_results:
        if desired_item in item.text:
            desired_item_div = item

    # check if the desired item is on sale 
    # note: we assume a Superstore item is on sale IFF its limit div contains text
    limit_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[2]")
    if (limit_div.text): # IFF
        # get the price. example of limit_div.text: "$4.29 LIMIT 4"
        price = limit_div.text.split()
        price = price[0]
        price = price.replace("$", "")
        print("This food is on sale: " + superstore_foods_randomized[i].search)
        print("The price is: " + price)
    else:    
        print("This food is not on sale: " + superstore_foods_randomized[i].search)
        print("No LIMIT. Moving on to the next item...")
        continue

stall()
driver.quit()
