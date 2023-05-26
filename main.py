# TODO: add try/catches to prevent popup from crashing program
# TODO: make a script to download the latest chromedriver.exe
# TODO: testing
# 1. test helper functions (ex. price parser)
# 2. test Selenium interactions (via Selenium's own testing framework or 'pytest')
# 3. you can test Superstore without depending on Superstore by using libraries like 'unittest.mock' and 'pytest-mock'
# CI/CD pipeline? test on every commit?

import random
from time import sleep
from sys import modules # gettatr()
from multiprocessing import Process

import urllib.robotparser

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import gspread

# Connect to Google Sheets API using gspread. 
# The variable "client" will be used to interact with Google Sheets.
credentials_path = "D:\Programming\Projects\selenium-groceries/credentials.json"
client = gspread.service_account(filename = credentials_path)

database = client.open("Grocery Database")
database_range = "A2:G"

stores = []
for worksheet in database.worksheets():
    stores.append(worksheet.title)

# Helper functions
def parse_robots_txt(store) -> (str | None):
    """
    Return website crawl delay from robots.txt (if any).
    """
    robots_txt_url = store.url + "robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_txt_url)
    rp.read()

    delay = rp.crawl_delay("*")
    return delay

def stall(delay: str) -> None:
    """
    Stall webdriver execution to conform with robots.txt.
    """
    if delay:
        sleep(int(delay))
    else:
        sleep(random.randint(3, 7))

############### CLASS SUPERSTORE ####################

class Superstore:
    url = "https://www.realcanadiansuperstore.ca/"

    def popup(driver) -> WebElement:
        return driver.find_element(By.CLASS_NAME, "modal-dialog__content__close")

    def search_bar(driver) -> WebElement:
        return driver.find_element(By.CLASS_NAME, "search-input__input")

    def search_results(driver) -> list[WebElement]:
        return driver.find_elements(By.CLASS_NAME, "product-tile__details__info")

    def is_sale(filtered_item: WebElement) -> bool:
        # checks for presence of a "badge", which indicates sale
        badge_text = filtered_item.find_element(
            By.CLASS_NAME, "product-tile-deal-badge"
        ).text
        if badge_text:
            print("Badge found!")
            return True
        else:
            print("Badge not found.")
            return False

    def parse_price(filtered_item: WebElement) -> float:
        try:
            price = filtered_item.find_element(
                By.CSS_SELECTOR,
                ".product-badge__text.product-badge__text--product-tile",
            ).text.lower()
            if "limit" in price:
                # ex. format: $4.29 LIMIT 4
                price_array = price.split()
                price = float(price_array[0].replace("$", ""))
            elif "for" in price:
                # ex. format: 2 FOR $9.00
                price_array = price.split()
                divisor = float(price_array[0])
                price = float(price_array[2].replace("$", ""))
                price = float(f"{(price/divisor):.2f}")
            return price
        except NoSuchElementException:
            print(
                "Sale price not found. Badge or Price selector is incorrect. Moving on to the next item..."
            )
            return -1

    def regular_price(filtered_item: WebElement) -> float:
        regular_price = filtered_item.find_element(
            By.CSS_SELECTOR, ".selling-price-list.selling-price-list--product-tile"
        ).text
        # ex. formats: $6.69ea, $11.49c01
        regular_price = regular_price.replace("$", "")
        regular_price = float(regular_price[0 : regular_price.index(".") + 3])
        return regular_price


############## CLASS NO FRILLS ##################

class NoFrills:
    url = "https://www.nofrills.ca/"

    def popup(driver) -> WebElement:
        return driver.find_element(By.CLASS_NAME, "modal-dialog__content__close")

    def search_bar(driver) -> WebElement:
        return driver.find_element(By.CLASS_NAME, "search-input__input")

    def search_results(driver) -> list[WebElement]:
        return driver.find_elements(By.CLASS_NAME, "product-tile__details__info")

    def is_sale(filtered_item: WebElement) -> bool:
        # checks for presence of a "badge", which indicates sale
        badge_text = filtered_item.find_element(
            By.CLASS_NAME, "product-tile-deal-badge"
        ).text
        if badge_text:
            print("Badge found!")
            return True
        else:
            print("Badge not found.")
            return False

    def parse_price(filtered_item: WebElement) -> float:
        try:
            price = filtered_item.find_element(
                By.CSS_SELECTOR,
                ".product-badge__text.product-badge__text--product-tile",
            ).text.lower()
            if "min" in price or "max" in price:  # format: "$4.29 MAX 4 / $5.00 MIN 2"
                price_array = price.split()
                price = price_array[0]
                price = float(price.replace("$", ""))
            elif "save" in price:
                price = filtered_item.find_element(
                    By.CSS_SELECTOR,
                    ".price__value.selling-price-list__item__price.selling-price-list__item__price--now-price__value",
                ).text
                price = float(price.replace("$", ""))
            return price
        except NoSuchElementException:
            print(
                "Sale price not found. Badge or Price selector is incorrect. Moving on to the next item..."
            )
            return -1

    def regular_price(filtered_item: WebElement) -> float:
        regular_price = filtered_item.find_element(
            By.CSS_SELECTOR,
            ".price__value.selling-price-list__item__price.selling-price-list__item__price--now-price__value",
        ).text
        regular_price = float(regular_price.replace("$", ""))
        return regular_price


############ SHOPPING LIST LOGIC ##############
# TODO: sales type
def create_shopping_list(sales) -> None:
    try:
        shopping_sheet = client.open("Shopping List (Louie)").sheet1
        shopping_sheet.clear()
    except gspread.exceptions.SpreadsheetNotFound:
        shopping_sheet = client.create("Shopping List (Louie)")
        shopping_sheet.share("goldjet32@gmail.com", perm_type="user", role="writer")
        shopping_sheet = client.open("Shopping List (Louie)").sheet1

    shopping_titles_range = "A1:E1"
    titles = ["URL", "Item", "Regular Price", "Current Price", "Cheapest Price"]
    shopping_sheet.update(shopping_titles_range, [titles])

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

    for item in sales:
        url = item[0]
        item_name = item[1]
        regular_price = item[4]
        current_price = item[7]
        cheapest_price = item[6]
        new_row = [url, item_name, regular_price, current_price, cheapest_price]
        shopping_sheet.append_row(new_row)

    # format the spreadsheet
    shopping_sheet.columns_auto_resize(1, 4)  # exclude the URL to keep it small
    shopping_sheet.format(
        [shopping_titles_range], {"textFormat": {"fontSize": 10, "bold": True}}
    )


# Step 0: Import the Grocery Database from Google Sheets into a CSV list, superstore_items.
# each item in superstore_items contains the following values:
# item[0] = item_url
# item[1] = item_name
# item[2] = search
# item[3] = search_filter
# item[4] = regular_price
# item[5] = max_buy_price
# item[6] = cheapest_price


def scrape(store: str) -> list:
    sales = []
    worksheet = database.worksheet(store)
    items = worksheet.get_values(database_range)
    random.shuffle(items)  # human behaviour

    # Convert the store name (str) to the corresponding Class
    store = getattr(modules[__name__], store)

    new_tab = "chrome://newtab"
    WEBDRIVER_PATH = "D:\Programming\Projects\selenium-groceries\chromedriver.exe"
    delay = parse_robots_txt(store)

    # Context manager ('with') will automatically handle quitting
    # A context manager has the attrs __enter__ and __exit__, so
    # to confirm that driver is a context manager, use hasattr(driver, '__exit__')
    with webdriver.Chrome(WEBDRIVER_PATH) as driver:
        driver.implicitly_wait(5)
        driver.get(new_tab)
        driver.maximize_window()  # human behaviour
        stall(delay)
        driver.get(store.url)
        stall(delay)

        # Eliminate any popups
        try:
            popup = store.popup(driver)
            popup.click()
        except NoSuchElementException:
            pass

        for item in items:
            # define variables, as specified in Step 0
            item_url = item[0]
            item_name = item[1]
            search = item[2]
            search_filter = item[3]
            regular_price = item[4]
            max_buy_price = float(item[5])

            # this try except block is necessary to cover some strange behaviour that occurs when
            # all initial cheapest_price (last column) fields are set to nothing.
            try:
                cheapest_price = float(item[6])
            except IndexError:
                item.append("")
                cheapest_price = ""
            except ValueError:
                cheapest_price = ""

            # Step 1: Engage with search bar
            search_bar = store.search_bar(driver)
            search_bar.click()
            search_bar.clear()
            stall(delay)
            search_bar.send_keys(search)
            stall(delay)

            search_bar.send_keys(Keys.RETURN)

            # Step 2: Filter search results to extract desired item
            # combing through too many search results may match an unrelated item that happens to share the search_filter.
            # therefore, introduce a search cap.
            filtered_item = None
            search_results = store.search_results(driver)
            search_cap = 8
            i = 0
            while i < min(len(search_results), search_cap):
                if search_filter in search_results[i].text:
                    filtered_item = search_results[i]
                    break
                else:
                    i += 1

            if filtered_item == None:
                print(
                    f"{search.upper()} not found in the search results. Moving on to the next item..."
                )
                stall(delay)
                continue

            # Step 3: Determine if the filtered item is on sale.
            if store.is_sale(filtered_item):
                price = store.parse_price(filtered_item)
                if price == -1:
                    continue
            else:  # item is not on sale: update regular price
                regular_price = store.regular_price(filtered_item)

                # update the database
                item_cell = worksheet.find(search)
                regular_price_cell = "E" + str(item_cell.row)
                worksheet.update(regular_price_cell, regular_price)

                # update the item
                item[4] = regular_price

                print(f"{search.upper()} is not on sale. Moving on to the next item...")
                stall(delay)
                continue

            # Step 4: Compare the price to the max_buy_price.
            if price <= max_buy_price:
                print(f"{search.upper()} is on sale! Adding to the Shopping List...")
                item.append(
                    price
                )  # saving the price so we can access it later as current_price

                # if the cheapest price wasn't inputted, OR price is the cheapest yet seen...
                if (cheapest_price == "") or (price < cheapest_price):
                    # update the database
                    item_cell = worksheet.find(search)
                    cheapest_price_cell = "G" + str(item_cell.row)
                    worksheet.update(cheapest_price_cell, price)
                    # update the item
                    item[6] = price

                sales.append(item)

            elif price > max_buy_price:
                print(
                    f"{search.upper()} is on sale, but still too expensive to buy. Moving on to the next item..."
                )
                stall(delay)
                continue
            stall(delay)
        return sales


############# MAIN #################
def main(store):
    sales = scrape(store)
    create_shopping_list(sales)


# multiprocessing
if __name__ == "__main__":
    for store in stores:
        Process(target=main, args=(store,)).start()
