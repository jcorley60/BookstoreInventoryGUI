#!/usr/bin/python -O
# InventoryInterfaceClasses.py - this file contains interface classes which are used to grab data
# from the DB for use directly w/ the GUI.
# MySQL database connection GUI via DAO; uses tkinter, mysql.connector
# Author: Joel Corley


class Author:
    """This class holds onto/processes 3 pieces of info from getAuthorData in InventoryDAO:
    an Author's name (first, last) and their respective assigned author number."""

    def __init__(self, cursorObject):
        self.cursorObject = cursorObject
        self.authList, self.authorNumbers = [], []
        self.processAuthorData()

    def __str__(self):
        """Provides author's firstname, and lastname for the GUI."""
        # return f"{self.first_name} {self.last_name}"
        return f"{self.authList}"

    def processAuthorData(self):
        """Takes getAuthorData cursor object as an argument and converts to list
        w/ these columns AUTHOR_NUM, AUTHOR_FIRST, AUTHOR_LAST"""
        for row in self.cursorObject:
            auth_id = row[0]
            first_name = row[1]
            last_name = row[2]
            self.authList.append(f"{first_name} {last_name}")
            self.authorNumbers.append(int(auth_id))
        return self.authList, self.authorNumbers


class Book:
    def __init__(self, cursorObject):
        self.cursorObject = cursorObject
        self.bookList, self.bookCodes = [], []
        self.processBookData()

    def __str__(self):
        """Provides book's title for the GUI."""
        return f"{self.bookList}"

    def processBookData(self):
        """"""
        for row in self.cursorObject:
            book_code = row[0]
            book_title = row[1]
            book_price = row[2]
            self.bookList.append((book_title, book_code, float(book_price)))
        return self.bookList


class Inventory:
    def __init__(self, cursorObject):
        self.cursorObject = cursorObject
        self.branchInfo = []
        self.processBranchData()

    def __str__(self):
        """Provides book's title."""
        return f"{self.branchInfo}"

    def processBranchData(self):
        """"""
        for row in self.cursorObject:
            branch_name = row[1]
            on_hand = row[2]
            self.branchInfo.append((branch_name, int(on_hand)))
        return self.branchInfo


class Category:
    def __init__(self, cursorObject):
        self.cursorObject = cursorObject
        self.categoryList, self.catList = [], []

    def processCategories(self):
        for row in self.cursorObject:
            categories = row[0]
            self.categoryList.append(categories)
        return self.categoryList

    def processCategoricalData(self):
        for row in self.cursorObject:
            book_code = row[0]
            book_title = row[1]
            book_price = row[2]
            self.catList.append((book_title, book_code, float(book_price)))
        return self.catList


class Publisher:
    def __init__(self, cursorObject):
        self.cursorObject = cursorObject
        self.publisherList, self.pubList = [], []

    def processPublishers(self):
        for row in self.cursorObject:
            categories = row[0]
            self.publisherList.append(categories)
        return self.publisherList

    def processPublisherData(self):
        for row in self.cursorObject:
            book_title = row[0]
            book_code = row[1]
            book_price = row[2]
            book_publisher = row[3]
            self.pubList.append((book_title, book_code, float(book_price), book_publisher))
        return self.pubList


