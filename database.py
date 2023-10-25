import sqlite3
from sqlite3 import Error

# TODO: *Raise* exceptions instead of printing & returning something is better practice?
# TODO: Is there a better convention than to return bools for OnSuccess and OnFailure?


def connect_to_db(path: str) -> sqlite3.Connection:
    """
    Connect to a SQLite database.
    Note that if the file does not exist, its creation will be handled automatically by SQLite.

    Params:
        path (str): the file location of the database.

    Returns:
        -sqlite3.Connection: A connection to the "prices.db" database upon success.
        -None: upon failure.

    """

    try:
        connection = sqlite3.connect(path)
        print(f"Connection to {path} successful.")
        return connection
    except Error as e:
        print(f"Error connecting to {path}: {e}")
        return None


def execute_query(connection: sqlite3.Connection, query: str) -> bool:
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        connection.commit()  # TODO: If I'm using the context manager, is this line necessary?
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return False


def execute_many_query(connection: sqlite3.Connection, query: str, params: list[tuple]) -> bool:
    cursor = connection.cursor()

    try:
        cursor.executemany(query, params)
        connection.commit()  # TODO: If I'm using the context manager, is this line necessary?
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return False


def execute_read_query(connection: sqlite3.Connection, query: str, params=()) -> list:
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        # It's possible to just return the cursor, and have the client iterate manually, ex.

        # for row in cursor:
        #   ...

        # That method is actually more performant due to lazy evaluation. However, I've
        # opted for .fetchall() since it results in cleaner/more transparent code client-side.
        return cursor.fetchall()

    except Error as e:
        print(f"Error executing query: {e}")
        return None


def insert_price_history(connection: sqlite3.Connection, price_data: list[tuple]) -> None:
    insert_price_history = """
    INSERT INTO 
        price_history (price, is_sale, timestamp, product_url)
    VALUES
        (?, ?, DATE("now"), ?)
    """

    execute_many_query(connection, insert_price_history, price_data)


def retrieve_stores(connection: sqlite3.Connection) -> list[str]:
    retrieve_stores = """
    SELECT name 
    FROM store
    """

    tuples = execute_read_query(connection, retrieve_stores)
    # sample return: [('Superstore',), ('No Frills',)]

    # convert to list of strings using list comprehension
    stores = [str(t[0]) for t in tuples]
    return stores


def retrieve_product_urls(connection: sqlite3.Connection, store: str) -> list[str]:
    """
    Retrieve all the product URLs from the database.

    Params:
        connection (sqlite3.Connection): a connection to the database.

    Returns:
        -list: a list of product URLs upon success.
        -None: upon failure.

    """

    retrieve_product_urls = """
    SELECT url 
    FROM product 
    WHERE store_name = ?
    """

    tuples = execute_read_query(connection, retrieve_product_urls, (store,))
    product_urls = [str(t[0]) for t in tuples]
    return product_urls


def retrieve_avg_price(connection: sqlite3.Connection, product_url: str) -> float:
    retrieve_avg_price = """
    SELECT price 
    FROM price_history 
    WHERE product_url = ?
    """

    tuples = execute_read_query(connection, retrieve_avg_price, (product_url,))
    prices = [float(t[0]) for t in tuples]
    avg_price = sum(prices)/len(prices)
    return avg_price


def retrieve_avg_sale_price(connection: sqlite3.Connection, product_url: str) -> float:
    retrieve_avg_sale_price = """
    SELECT price 
    FROM price_history 
    WHERE is_sale = TRUE AND product_url = ?
    """

    tuples = execute_read_query(
        connection, retrieve_avg_sale_price, (product_url,))
    prices = [float(t[0]) for t in tuples]
    avg_price = sum(prices)/len(prices)
    return avg_price
