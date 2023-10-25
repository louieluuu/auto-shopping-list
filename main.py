import os
import yaml

from multiprocessing import Process, Manager

from database import connect_to_db
from database import create_db
from database import update_db
from database import retrieve_stores
from database import insert_price_history
from database import retrieve_avg_price
from database import retrieve_avg_sale_price

from scrape import scrape
# from mail import send_email


def main(store: str, shopping_dict: dict) -> None:
    if store in shopping_dict:
        print("ERROR: Why is this store already in the shopping_dict?")
        exit(-1)

    sales = []

    connection = connect_to_db("prices.db")

    with connection:
        # Step 1. Scrape store for price data
        price_data = scrape(connection, store)

        # Step 2. Insert price data into database
        insert_price_history(connection, price_data)

        # Step 3. Calculate the average price of each item
        for datum in price_data:
            # each price_datum is a tuple of form (price, is_sale, product_url)
            (price, is_sale, product_url) = datum
            avg_price = retrieve_avg_price(connection, product_url)

            # Step 4. Add worthy entries to the sales list
            if price < avg_price:
                entry = (product_url, price)
                sales.append(entry)

        # Step 5. Update the shopping_dict with the sales
        shopping_dict[store] = sales

    # connection context manager doesn't automatically close, so...
    connection.close()


# With Multiprocessing, we can scrape many stores simultaneously
# using multiple browsers in parallel.
if __name__ == "__main__":
    ##############################
    #           Config           #
    ##############################

    # Load the config file
    with open("config_private.yaml", "r") as file:
        config = yaml.safe_load(file)

    email = config.get("email")
    stores_and_products = config.get("stores")

    # If prices.db doesn't exist yet, create a new database using the config file
    cwd = os.getcwd()
    if not os.path.exists(f"{cwd}/prices.db"):
        print("Initializing first-time setup...")
        create_db(stores_and_products)
        print("Setup complete!")

    else:
        # Check if config.yaml has been modified; if so, update the database
        curr_modified = os.path.getmtime("config_private.yaml")
        last_modified = config.get("last_modified")

        if curr_modified != last_modified:
            print("Changes detected in config.yaml.")
            print("Updating database...")
            update_db(stores_and_products)
            print("Update complete!")

            # TODO:
            print("List of changes: ")

    ##############################
    #       Multiprocessing      #
    ##############################
    processes = []
    shopping_list = []
    stores = []

    connection = connect_to_db("prices.db")
    stores = retrieve_stores(connection)
    connection.close()

    # Create a dictionary with Manager to be shared by all processes
    with Manager() as manager:
        shopping_dict = manager.dict()

        for store in stores:
            p = Process(target=main, args=(store, shopping_dict))
            processes.append(p)
            p.start()

        # Wait for all processes to complete before proceeding
        for p in processes:
            p.join()

        # Construct a final shopping list from the shared shopping_dict
        for store in shopping_dict:
            # If there were no sales at a store, shopping_dict[store] is empty
            if not shopping_dict[store]:
                print(f"No sales found at {store}.")
            else:
                shopping_list.append(shopping_dict[store])

    for store_results in shopping_list:
        print(store_results)
        print("\n")

    # TODO:
    # send_email(shopping_list)
