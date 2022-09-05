# -Retrieve price of certain items of interest (predetermined by list) from grocery wesbites: T&T, Superstore, Walmart.
#     -unclear if the URLs of items will stay the same over time, may have to use search function instead?
# -Checks if the prices fall below a certain threshold, again, predetermined by the user.    
# -If so, prints out item names and prices in readable list form, sorted by store. This is now the "Shopping List".
# -Somehow make the Shopping List accessible via mobile device (consider e-mail, perhaps an app?)

import unittest #for testing

#standard selenium imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#wait imports
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

url = "https://www.walmart.ca/en/ip/folgers-black-silk-ground-coffee-641-g/6000205233378"

# T&T 40lbs jasmine rice: "https://www.tntsupermarket.com/eng/75551501-tnt-thai-jasmine-rice-40lb.html"
    # EC.presence_of_element_located((By.CLASS_NAME, "productFullDetail-productPrice-1Js"))
# Superstore lentils: "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA"
    # EC.presence_of_element_located((By.CLASS_NAME, "selling-price-list__item"))
# Walmart coffee: "https://www.walmart.ca/en/ip/folgers-black-silk-ground-coffee-641-g/6000205233378"
    
driver.get(url)

print("test1\n")

try:
    element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "css-k008qs e1ufqjyx0"))
    )    
except:
    driver.quit()


#text = element.get_attribute("textContent")
print(element.text)

print("test2\n")
# element.click()
# element.send_keys(Keys.ENTER)

# driver.get("http://www.python.org")
# elem = driver.find_element(By.CLASS_NAME, "search-field")

# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)


# time.sleep(10) #delays program's execution by 10 seconds. nifty