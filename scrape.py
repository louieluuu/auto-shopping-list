import random
from time import sleep
from sys import modules  # getattr()

import urllib.robotparser
import sqlite3
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from database import retrieve_product_urls

# These imports are necessary even though they're grayed out.
# The Classes are being used indirectly via getattr().
from stores.Superstore import Superstore
from stores.NoFrills import NoFrills


# # Eliminate any popups
# try:
#     popup = Store.popup(driver)
#     popup.click()
# except NoSuchElementException:
#     pass


# Helper functions


def parse_robots_txt(url: str) -> (str | None):
    """
    Return website crawl delay from robots.txt.
    """
    robots_txt_url = f"{url}robots.txt"
    print(robots_txt_url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()

    delay = rp.crawl_delay("*")
    return delay


def stall(delay: str) -> None:
    """
    Stall webdriver execution according to robots.txt.
    """
    if delay:
        sleep(int(delay))
    else:
        sleep(random.randint(3, 7))


def scrape(connection: sqlite3.Connection, store: str) -> list[tuple]:
    """
    Scrape all product URLs in the database associated with a store.

    Params:
        store (str): the name of the store to scrape.

    Returns:
        -list[tuple]: a list of rows containing price data.\n
        ex. (price, is_sale, product_url)\n
        (3.99, "TRUE", "http://...")

    """
    price_data = []

    # Convert the store name (str) to the corresponding Class
    Store = getattr(modules[__name__], store)

    delay = parse_robots_txt(Store.url)
    new_tab = "chrome://newtab"
    WEBDRIVER_PATH = "./chromedriver.exe"

    # Brave browser
    BRAVE_PATH = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    options = webdriver.ChromeOptions()
    options.binary_location = BRAVE_PATH
    options.add_argument("--headless")

    with webdriver.Chrome(executable_path=WEBDRIVER_PATH, chrome_options=options) as driver:

        # with webdriver.Chrome(WEBDRIVER_PATH) as driver:
        # TODO: Download webdriver automatically (JSON endpoints).

        driver.implicitly_wait(5)
        driver.get(new_tab)
        driver.maximize_window()  # human behaviour

        product_urls = retrieve_product_urls(connection, store)

        for product_url in product_urls:
            driver.get(product_url)

            # Try to find a sale first, else just grab the regular price.
            is_sale = True
            price = Store.parse_sale_price(driver)
            if price == -1:
                is_sale = False
                price = Store.parse_regular_price(driver)
                if price == -1:
                    print("Error: Price could not be processed.")
                    return

            row = (price, is_sale, product_url)
            price_data.append(row)

            stall(delay)

    return price_data
