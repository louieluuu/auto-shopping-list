# ~~~~~~~~~ SELENIUM ~~~~~~~~~~~#

# syntax for explicit wait - should be obsolete due to implicit wait
    try:
        element = WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CLASS_NAME, "price"))
        )
        stall()
    except:
        print("Element not found. Quitting now...")
        driver.quit()


# if element.text doesn't work, use this instead:
    text1 = element.get_attribute("textContent")
    print(text1)


# CSS_SELECTOR can be used for multiple classes. just remember to include a "." at the front too.
# in this example, By.CLASS_NAME, "searchlink.js searchlink" would not work due to CLASS_NAME selecting just one class.
    element = driver.find_element(By.CSS_SELECTOR, ".searchlink.js-searchlink") 


# for Chromedriver, if the element is wrapped in a span, it won't work with click().
# instead, just use RETURN:
    send_keys(Keys.RETURN)



# ~~~~~~~~ XPATH ~~~~~~~~~ #

# after you've found a matching div element, you can use the following XPATH syntax 
# to grab the sibling (i.e. usually where the price is located) 
# note: I believe you have to replace "div" with whatever tag the sibling falls under
    (By.XPATH, "./following-sibling::div]") 
    

# to traverse downwards in an XPATH, you write "/" followed by "div[x]",
# where x is the number of divs you want to traverse.
# in Chrome: F12 -> right click parent -> collapse children for a clearer tree.
    (By.XPATH, "./following-sibling::div/div[2]")



