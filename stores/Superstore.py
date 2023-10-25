from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

sale_price = "product-promo__badge-wrapper"
regular_price = "selling-price-list__item"


class Superstore:
    url = "https://www.realcanadiansuperstore.ca/"

    @staticmethod
    def parse_sale_price(driver: WebDriver) -> float:
        try:
            price = driver.find_element(By.CLASS_NAME, sale_price).text

            if "MAX" in price or "MIN" in price:
                # ex. format: $4.29 MAX 4 / $5.00 MIN 2
                price_array = price.split()
                price = float(price_array[0].replace("$", ""))
            elif "FOR" in price:
                # ex. format: 2 FOR $9.00
                price_array = price.split()
                divisor = float(price_array[0])
                price = float(price_array[2].replace("$", ""))
                price = float(f"{(price/divisor):.2f}")
            elif "SAVE" in price:
                # ex. format: SAVE $0.51
                # This particular label is weird, because Superstore actually changes the regular price class
                # to be the sale price - so we can just use the regular price method we've created.
                # We aren't using the label information at all, besides that it has "SAVE" in the title.
                price = Superstore.parse_regular_price(driver)
            else:
                print("ERROR: Price logic changed. Update required.")
            return price

        except NoSuchElementException:
            print(
                "Sale price not found."
            )
            return -1

    @staticmethod
    def parse_regular_price(driver: WebDriver) -> float:
        try:
            price = driver.find_element(By.CLASS_NAME, regular_price).text

            # ex. formats: $6.69ea, $11.49c01
            price = price.replace("$", "")
            price = float(
                price[0:price.index(".") + 3])
            return price

        except NoSuchElementException:
            print(
                "ERROR: Regular price not found. Updated required."
            )
            return -1
