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

new_tab = "chrome://newtab"
tnt_url = "https://www.tntsupermarket.com/eng/75551501-tnt-thai-jasmine-rice-40lb.html" # T&T is being weird, searching
# "t&t thai jasmine rice" won't return any results on the headless browser. additionally, visiting the link directly will 
# show a difference price ($43.xx) than the price on a normal browser ($46.19)
superstore_url = "https://www.realcanadiansuperstore.ca/"
    
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

# engage with search bar
search = "red split lentils"

search_bar = driver.find_element(By.CLASS_NAME, "search-input__input") 
search_bar.click()
search_bar.send_keys(search)
stall()
search_bar.send_keys(Keys.RETURN)

# find desired item from search results
desired_item = "1.8 kg"
search_results = driver.find_elements(By.TAG_NAME, "h3")

for item in search_results:
    if desired_item in item.text:
        desired_item_div = item

# check if the desired item is on sale 
# note: we assume a Superstore item is on sale IFF it has a limit div.
try: 
    limit_div = desired_item_div.find_element(By.XPATH, "./following-sibling::div/div[2]")
except:
    print("No sale. Moving on to the next item...")

# get the price. example of price_div.text: "$4.29 LIMIT 4"
price = limit_div.text.split()
price = price[0]
price = price.replace("$", "")
print(price)

stall()

driver.quit()
quit()