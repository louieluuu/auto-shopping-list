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