#!/usr/bin/python -O
# InventoryDAO.py - creates the Henry DB DAO intermediary
# MySQL database connection GUI via DAO; uses tkinter, mysql.connector
# Author: Joel Corley

import yaml
import mysql.connector
from InventoryInterfaceClasses import Author, Book, Inventory, Category, Publisher


class inventoryDAO:
    """Class representing the Data Access Object (DAO) which is an intermediary between the DB & the GUI.
    The DAO separates the GUI & database, allowing either to be changed out w/out redoing code.
    The database connector cursor resides w/in this DAO, only.

    DB connection: interacts w/ DB; retrieves data.
    The cursor object is filled with the SQL statement return result and needs to be processed via
    'InventoryInterfaceClasses.py' for use w/ the GUI in the creation of lists, etc.

    This DAO keeps the DB connection open the entire time the GUI is active.

    Numerous errata have been discovered in the underlying database: no attempt has been made to make corrections,
    rather the strategy was to make the code robust enough to handle issues without breaking.
    """
    def __init__(self):
        """"""
        self.creds = self.get_credentials()
        self.usr, self.pw, self.db = self.creds['user'], self.creds['password'], self.creds['database']
        self.mydb = mysql.connector.connect(            # database create connection
            user=self.usr,
            password=self.pw,
            database=self.db,
            host='127.0.0.1',    # localhost IP, for db on local machine
        )
        self.mycur = self.mydb.cursor()                 # create cursor object which holds results from SQL queries
        self.authorsList, self.bookList, self.indexList, self.branchInfo = [], [], [], []

    def get_credentials(self):
        """Get credentials from file: username, password, db for SQL database."""
        with open('config.yaml', 'r') as config_file:
            self.config = yaml.safe_load(config_file)
        return self.config

    def close(self):
        """Closes DB connection"""
        self.mydb.close()                           # closes connection

    def getAuthorData(self):
        """This method gets the author data, by executing a query on the database which brings back the author info.
        This info includes author [unique identifying] number and author name (first, last)."""
        # Perform the query
        sqlStatement = """SELECT a.AUTHOR_NUM, AUTHOR_FIRST, AUTHOR_LAST 
                            FROM HENRY_AUTHOR a
                            JOIN HENRY_WROTE w
                            ON a.AUTHOR_NUM = w.AUTHOR_NUM
                            JOIN HENRY_INVENTORY i
                            ON w.BOOK_CODE = i.BOOK_CODE
                            GROUP BY a.AUTHOR_NUM
                            ORDER BY AUTHOR_LAST;"""            # create SQL statement
        self.mycur.execute(sqlStatement)                        # execute statement; self.mycur now holds query results
        # instantiate Author class to process/present author list + author numbers
        self.authorsList, self.indexList = Author(self.mycur).processAuthorData()
        return self.authorsList, self.indexList

    def getBookData(self, authorID=14):
        """This method gets book_code, book_title & book price by executing a query on the database which brings back
        the book info retrieved via the cursor object; which then needs to be processed via .processBookData()"""
        sqlStatement = f"""SELECT b.BOOK_CODE, TITLE, PRICE 
                            FROM HENRY_BOOK b        
                            JOIN HENRY_WROTE w
                            ON b.BOOK_CODE = w.BOOK_CODE
                            JOIN HENRY_AUTHOR a
                            ON a.AUTHOR_NUM = w.AUTHOR_NUM
                            WHERE a.AUTHOR_NUM = {authorID}
                            ORDER BY TITLE;"""                  # create SQL stmnt
        self.mycur.execute(sqlStatement)                        # execute statement; self.mycur now holds query results
        self.bookList = Book(self.mycur).processBookData()      # instantiate Book class to present author list
        return self.bookList

    def getBranchData(self, bookCode='6328'):
        sqlStatement = f"""SELECT BOOK_CODE, BRANCH_NAME, ON_HAND 
                            FROM HENRY_INVENTORY i
                            JOIN HENRY_BRANCH b
                            ON i.BRANCH_NUM = b.BRANCH_NUM
                            WHERE BOOK_CODE = '{bookCode}';"""
        self.mycur.execute(sqlStatement)                    # execute statement; self.mycur now holds query results
        # instantiate Inventory class to present branch inventory info
        self.branchInfo = Inventory(self.mycur).processBranchData()
        return self.branchInfo

    def getCategories(self):           # DISTINCT() may be more common in SQL, generally, but DISTINCT TYPE also works
        sqlStatement = """SELECT DISTINCT(TYPE)          
                            FROM HENRY_BOOK
                            ORDER BY TYPE;"""                                               # create SQL stmnt
        self.mycur.execute(sqlStatement)                        # execute statement; self.mycur now holds query results
        # instantiate Category class to present book category list
        categories = Category(self.mycur).processCategories()
        return categories

    def getCategoricalBooks(self, category='ART'):
        sqlStatement = f"""SELECT BOOK_CODE, TITLE, PRICE 
                            FROM HENRY_BOOK
                            WHERE TYPE = '{category}'
                            ORDER BY TITLE;"""  # create SQL stmnt
        self.mycur.execute(sqlStatement)  # execute statement; self.mycur now holds query results
        # instantiate Category class to present book category list
        categories = Category(self.mycur).processCategoricalData()
        return categories

    def getPublishers(self):
        sqlStatement = """SELECT DISTINCT(PUBLISHER_NAME) 
                            FROM HENRY_BOOK b
                            JOIN HENRY_PUBLISHER p
                            ON b.PUBLISHER_CODE = p.PUBLISHER_CODE
                            ORDER BY PUBLISHER_NAME;"""  # create SQL stmnt
        self.mycur.execute(sqlStatement)  # execute statement; self.mycur now holds query results
        # instantiate Category class to present book category list
        publishers = Publisher(self.mycur).processPublishers()
        return publishers

    def getPublisherBooks(self, publisher='Back Bay Books'):
        """Appears to be an issue w/ unique books codes for books 'Black House', 'Treasure Chest', and
        'Van Gogh and Gauguin'."""
        sqlStatement = f"""SELECT TITLE, b.BOOK_CODE, PRICE, PUBLISHER_NAME 
                            FROM HENRY_BOOK b
                            JOIN HENRY_PUBLISHER p
                            ON b.PUBLISHER_CODE = p.PUBLISHER_CODE
                            WHERE p.PUBLISHER_NAME = '{publisher}'
                            ORDER BY PUBLISHER_NAME, TITLE;"""  # create SQL stmnt
        self.mycur.execute(sqlStatement)  # execute statement; self.mycur now holds query results
        # instantiate Publisher class to present books by publisher list
        categories = Publisher(self.mycur).processPublisherData()
        return categories


