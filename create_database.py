from database import connect_to_db, execute_query

# Create tables
create_store_table = """
CREATE TABLE store (
    name TEXT PRIMARY KEY
)
"""

create_product_table = """
CREATE TABLE product (
    url TEXT PRIMARY KEY,
    name TEXT,

    store_name TEXT,
    FOREIGN KEY(store_name) REFERENCES store(name)
)
"""

create_price_history_table = """
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price REAL,
    is_sale INTEGER,
    timestamp TEXT, 
    
    product_url TEXT,
    FOREIGN KEY(product_url) REFERENCES product(url)
)
"""

# Insert
insert_stores = """
INSERT INTO 
    store (name)
VALUES
    ("Superstore"),
    ("No Frills")
"""

insert_products = """
INSERT INTO
    product (url, name, store_name)
VALUES
    ("https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA", "Red Split Lentils 1.8kg", "Superstore"),
    ("https://www.realcanadiansuperstore.ca/smooth-peanut-butter-club-size/p/20323398002_EA", "No Name Smooth Peanut Butter, Club Size 2kg", "Superstore"),
    ("https://www.realcanadiansuperstore.ca/lemon-lime-sports-drink-case/p/20303218004_C06", "Gatorade", "Superstore"),
    ("https://www.realcanadiansuperstore.ca/excellence-70-cacao-dark-chocolate-bar/p/20312527005_EA", "Lindt Chocolate Bar 70%", "Superstore"),

    ("https://www.nofrills.ca/red-split-lentils/p/20558862_EA", "Red Split Lentils 1.8kg", "No Frills"),
    ("https://www.nofrills.ca/smooth-peanut-butter-club-size/p/20323398002_EA", "No Name Smooth Peanut Butter, Club Size 2kg", "No Frills"),
    ("https://www.nofrills.ca/lemon-lime-sports-drink-case/p/20303218004_C06", "Gatorade", "No Frills"),
    ("https://www.nofrills.ca/excellence-70-cacao-dark-chocolate-bar/p/20312527005_EA", "Lindt Chocolate Bar 70%", "No Frills")
"""

### for testing only - dummy data ###
insert_price_history = """
INSERT INTO
    price_history (price, is_sale, timestamp, product_url)
VALUES
    (6.00, True, DATE("now"), "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA"),
    (8.49, False, DATE("now"), "https://www.realcanadiansuperstore.ca/smooth-peanut-butter-club-size/p/20323398002_EA"),
    (6.99, TRUE, DATE("now"), "https://www.realcanadiansuperstore.ca/lemon-lime-sports-drink-case/p/20303218004_C06"),
    (4.49, FALSE, DATE("now"), "https://www.realcanadiansuperstore.ca/excellence-70-cacao-dark-chocolate-bar/p/20312527005_EA"),
    
    (6.00, 0, DATE("now"), "https://www.nofrills.ca/red-split-lentils/p/20558862_EA"),
    (8.49, 0, DATE("now"), "https://www.nofrills.ca/smooth-peanut-butter-club-size/p/20323398002_EA"),
    (6.99, 0, DATE("now"), "https://www.nofrills.ca/lemon-lime-sports-drink-case/p/20303218004_C06"),
    (3.50, 1, DATE("now"), "https://www.nofrills.ca/excellence-70-cacao-dark-chocolate-bar/p/20312527005_EA"),

    (4.00, 1, DATE("now"), "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA"),
    (6.00, 0, DATE("now"), "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA"),
    (6.00, 0, DATE("now"), "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA"),
    (5.00, 1, DATE("now"), "https://www.realcanadiansuperstore.ca/red-split-lentils/p/20558862_EA")

"""


def main():
    connection = connect_to_db("prices.db")

    with connection:
        execute_query(connection, create_store_table)
        execute_query(connection, create_product_table)
        execute_query(connection, create_price_history_table)

        execute_query(connection, insert_stores)
        execute_query(connection, insert_products)

        ### for testing only - dummy data ###
        # execute_query(connection, insert_price_history)

    connection.close()


if __name__ == "__main__":
    main()
