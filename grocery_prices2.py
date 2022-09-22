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
url = "https://starforgesystems.com/"

# Newegg: "https://www.newegg.ca/samsung-1tb-980-pro/p/N82E16820147790?Item=N82E16820147790"

# T&T 40lbs jasmine rice: "https://www.tntsupermarket.com/eng/75551501-tnt-thai-jasmine-rice-40lb.html"
    # EC.presence_of_element_located((By.CLASS_NAME, "productFullDetail-productPrice-1Js"))
# Superstore lentils: "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA"
    # EC.presence_of_element_located((By.CLASS_NAME, "selling-price-list__item"))
# Walmart coffee: "https://www.walmart.ca/en/ip/folgers-black-silk-ground-coffee-641-g/6000205233378"
    # EC.presence_of_element_located((By.CLASS_NAME, "css-k008qs e1ufqjyx0"))
    
# Stalls program execution by 5-20 seconds to simulate human web-scrolling behaviour.  
def stall():
    time.sleep(random.randint(5,20))

driver.implicitly_wait(5) # wait max 5 seconds before executing commands with the driver, replaces need for explicit waits (allegedly)
                          # note that if the command fails ex. element not found, error won't be thrown because there's no try... except structure
driver.get(new_tab)
driver.maximize_window() # human behaviour

driver.get(url)

element = driver.find_element(By.CLASS_NAME, "recommendation-modal__close-button")
element.click()
element = driver.find_element(By.CSS_SELECTOR, ".searchlink.js-searchlink") # css_selector can be used for multiple classes, just remember
                                                                            # to include a "." at the front too.
element.click()
element = driver.find_element(By.CLASS_NAME, "search__input")
element.click()
time.sleep(2)

search = "horizon" # shouldn't be the exact name of the item - humans don't search up "Starforge Horizon Creator Edition PC"

element.send_keys(search)
time.sleep(2)
element.send_keys(Keys.RETURN)
time.sleep(2)

element = driver.find_elements(By.CLASS_NAME, "product-item__title")

for item in element:
    if "Creator" in item.text:
        element = item

sibling = element.find_element(By.XPATH, "./following-sibling::div")
price = sibling.text
price = price.replace("$", "").replace(",", "")
print(price)
driver.quit()

quit()


try:
    element = WebDriverWait(driver, 7).until(
        EC.presence_of_element_located((By.CLASS_NAME, "price"))
    )
    stall()
except:
    print("Element not found. Quitting now...")
    driver.quit()

# if element.text doesn't work, use this instead:
# text1 = element.get_attribute("textContent")
# print(text1)

print(element.text)

print("Price found. Quitting now...")

driver.quit()



##### just messing around with the API for the first time #####

# element.click()
# element.send_keys(Keys.ENTER)

# driver.get("http://www.python.org")
# elem = driver.find_element(By.CLASS_NAME, "search-field")

# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)


