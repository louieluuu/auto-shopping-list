from multiprocessing import Process, Manager

from database import connect_to_db
from database import retrieve_stores
from database import insert_price_history
from database import retrieve_avg_price
from database import retrieve_avg_sale_price
from scrape import scrape
from mail import send_email


def main(store: str, shopping_dict: dict) -> None:
    if store in shopping_dict:
        print("ERROR: Why is this store already in the shopping_dict? wat")
    shopping_dict[store] = []

    connection = connect_to_db("prices.db")

    with connection:
        # Step 1. Scrape store for price data
        price_data = scrape(connection, store)

        # Step 2. Insert price data into database
        insert_price_history(connection, price_data)

        # Step 3. Calculate the average price of each item
        for datum in price_data:
            # each price_datum is a tuple of form (price, is_sale, product_url)
            price = datum[0]
            is_sale = datum[1]
            product_url = datum[2]

            avg_price = retrieve_avg_price(connection, product_url)

            # Step 4. Add worthy entries to the shopping list
            if price < avg_price:
                entry = (product_url, price)
                shopping_dict[store].append(entry)

    # connection context manager doesn't automatically close, so...
    connection.close()


# With Multiprocessing, we can scrape many stores simultaneously
# using multiple browsers in parallel.
if __name__ == "__main__":
    processes = []
    shopping_list = []

    connection = connect_to_db("prices.db")
    stores = retrieve_stores(connection)
    connection.close()

    ##############################
    #       Multiprocessing      #
    ##############################

    # Create a dictionary with Manager to be shared by all processes
    with Manager() as manager:
        shopping_dict = manager.dict()
    for store in stores:
        p = Process(target=main, args=(store, shopping_dict))
        p.start()
        processes.append(p)

    # Wait for all processes to complete before proceeding
    for p in processes:
        p.join()

    # Create a final shopping list from the shared shopping_dict
    for store in shopping_dict:
        # If there were no sales at a store, shopping_dict[store] is empty
        if not shopping_dict[store]:
            print(f"No sales found at {store}. 😓")
        shopping_list.extend(shopping_dict[store])

    print(f"shopping_list: {shopping_list}")

    # TODO: HTML sending
    # send_email(shopping_list)
