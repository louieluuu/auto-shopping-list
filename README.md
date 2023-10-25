# Auto Shopping List

Auto Shopping List is an automation script that web scrapes prices of products, stores them in a database, and e-mails sales to the user. Upon initialization, the database retains price history of the items you specify, and can be used to inform purchase decisions in a fashion similar to [camelcamelcamel](https://www.camelcamelcamel.ca/).

Built with Python, Selenium, and SQLite.

## Features

- **Modular**: supports multiple websites through OOP-like design
- **Multiprocessing**: scrapes multiple stores simultaneously

## How to Use

Edit the *config.yaml* file that comes with the project. *config.yaml* contains easy-to-follow examples to guide you along.
In a word, all you have to do is provide URLs and names of the product you want to track! Everything else - including the creation and updating of the database - will be handled by the program.

## Database Schema

### ER Diagram

![er diagram xml drawio](https://github.com/louieluuu/auto-shopping-list/assets/112336312/6262398a-a97f-4e28-84d4-0e1cd91257c9)
