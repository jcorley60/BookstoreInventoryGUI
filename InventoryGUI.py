#!/usr/bin/python -O
# InventoryGUI - starts a GUI which sets up tabs using tkinter's Notebook for tab control
# MySQL database connection GUI via DAO; uses tkinter, mysql.connector
# Author: Joel Corley

import tkinter as tk
from tkinter import ttk
from InventoryDAO import inventoryDAO


# GUI
class createGUI:
    """Creates main tkinter GUI window w/ attached tab control."""
    def __init__(self):
        self.inventoryDAO = inventoryDAO()      # instantiate inventoryDAO class to make SQL queries; we only need 1 DB connection

        # Main window
        self.root = tk.Tk()
        self.root.title("Henry Bookstore Inventory")
        self.root.geometry('800x400')

        # Tab control
        self.tabControl = ttk.Notebook(self.root)   # Notebook used for creation of tabs
        self.tab1 = ttk.Frame(self.tabControl)  # tab1, tab2 & tab3 are tabs for Search by Author, Category & Publisher
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)

        # Add tab descriptors
        self.tabControl.add(self.tab1, text='Search by Author')
        self.tabControl.add(self.tab2, text='Search by Category')
        self.tabControl.add(self.tab3, text='Search by Publisher')
        self.tabControl.pack(expand=1, fill="both")

        # Fill out content of tabs by class instantiation of SearchByAuthor, SearchByClass, SearchByPublisher
        SBA(self.tab1, self.inventoryDAO)
        SBC(self.tab2, self.inventoryDAO)
        SBP(self.tab3, self.inventoryDAO)

        self.root.mainloop()    # method to run main window & its contents


class SBA:
    """Class representing Search by Author tab of GUI.
    Takes respective tkinter tab and DAO as arguments
    and then places content onto this particular tab which is annotated below."""
    def __init__(self, tab1, DAO):
        self.getBooks, self.getTree     # combobox functions
        self.bookIndex, self.branchList = 0, 0
        self.DAO = DAO

        # Labels for combo boxes/drop-down menus & book price
        self.lab1 = ttk.Label(tab1)
        self.lab1.grid(column=1, row=2)
        self.lab1['text'] = "Author Selection:"

        self.lab2 = ttk.Label(tab1)
        self.lab2.grid(column=7, row=2)
        self.lab2['text'] = "Book Selection:"

        self.lab3 = ttk.Label(tab1)
        self.lab3.grid(column=7, row=1)
        self.lab3['text'] = "Price:"

        # Comboboxes -- drop-down menu implementation of tkinter
        self.com1 = ttk.Combobox(tab1, width=40, state="readonly")
        self.com1.grid(column=1, row=3)
        authorList, self.authorNumbers = self.DAO.getAuthorData()
        print("Author List:\n", authorList)
        self.com1['values'] = authorList
        self.com1.current(0)
        # .bind finds author selected & gets associated book info:
        # when the combobox changes (i.e. event occurs), the callback function is executed
        self.com1.bind("<<ComboboxSelected>>", self.getBooks)     # .bind(event, action)

        self.com2 = ttk.Combobox(tab1, width=40, state="readonly")
        self.com2.grid(column=7, row=3)
        self.bookList = self.DAO.getBookData(authorID=14)
        tempList = list()
        [tempList.append(book[0]) for book in self.bookList]  # extract book titles, to list, from (title, code, price)
        self.com2['values'] = tempList
        self.com2.current(0)
        self.com2.bind("<<ComboboxSelected>>", self.getTree)

        # Price display label
        self.lab4 = ttk.Label(tab1, font=("Time New Roman", 20))        # make font larger for easy visibility
        self.lab4.grid(column=8, row=1)
        self.lab4['text'] = f"$ {float(self.bookList[0][2]):.2f}"           # autofill 1st book's price

        # Treeview - an embedded table w/in main frame
        self.tree1 = ttk.Treeview(tab1, columns=('BranchName', 'OnHand'), show='headings')
        self.tree1.heading('BranchName', text='Branch Name')
        self.tree1.heading('OnHand', text='Copies Available')
        self.tree1.grid(column=1, row=1)
        # Fill Treeview w/ values
        self.branchList = self.DAO.getBranchData()              # retrieve branch info for default book value
        for row in self.branchList:                           # autofill Tree w/ branch inventory info from 1st book
            self.tree1.insert("", "end", values=[row[0], row[1]])

    def getBooks(self, event):
        """For use with author combobox --
        This function is called when a selection is made in the author combo box in order to populate the book combobox,
        tree and price labels.
        As an item is selected from the dropdown it will print in the output window of the IDE for reference/testing.
        Note: selection of an item from the dropdown is considered an 'event' hence the reactionary function argument.
        """
        authIndex = event.widget.current()    # this provides the current list index/selection for the author list
        authID = self.authorNumbers[authIndex]   # convert from index location to authorID
        print("Author Index selected is: " + str(authID))
        self.bookList = self.DAO.getBookData(authorID=authID)       # retrieve new books
        print("\tBooks:", self.bookList)                            # print out book list for debugging/tracking/etc

        for i in self.tree1.get_children():          # When new author is picked -- remove old values in tree list
            self.tree1.delete(i)

        # fill combobox, tree, price defaults views
        tempList = list()
        [tempList.append(book[0]) for book in self.bookList]        # extract book title from (title, book_code, price)
        self.com2['values'] = tempList                              # pass title list to combobox
        self.com2.current(0)                        # make book retrieved by author, in location 0, the default view

        self.lab4['text'] = f"$ {float(self.bookList[0][2]):.2f}"   # autofill price based of 1st book
        # Autofill Treeview w/ 1st book values
        self.branchList = self.DAO.getBranchData(bookCode=self.bookList[0][1])
        print(f"\t---> branch inventory for '{self.bookList[0][0]}':", self.branchList)

        for row in self.branchList:
            self.tree1.insert("", "end", values=[row[0], row[1]])

    def getTree(self, event):
        """For use with book combobox --
        This function is called when a selection is made in the author combo box in order to populate the tree and
        price labels.
        As an item is selected from the dropdown it will print in the output window of the IDE for reference/testing.
        Note: selection of an item from the dropdown is considered an 'event' hence the reactionary function argument.
        """
        for i in self.tree1.get_children():  # Remove old values in tree
            self.tree1.delete(i)

        self.bookIndex = event.widget.current()     # get current book index
        bookCode = self.bookList[self.bookIndex]    # translate index into a book code
        print(f"""\tBook Index selected is {self.bookIndex}, Book Code is {bookCode[1]}, price is ${float(bookCode[2]):.2f}""")

        self.branchList = self.DAO.getBranchData(bookCode=bookCode[1])      # retrieve branch info for Tree
        print('\t---> branch inventory:', self.branchList)
        self.lab4['text'] = f"$ {float(bookCode[2]):.2f}"               # update price

        # Fill Treeview w/ values
        for row in self.branchList:
            self.tree1.insert("", "end", values=[row[0], row[1]])


class SBC:
    """Class representing Search by Category tab of GUI.
        Takes respective tkinter tab and DAO as arguments
        and then places content onto this particular tab."""
    def __init__(self, tab2, DAO):
        self.getBooks, self.getTree
        self.branchList = 0
        self.DAO = DAO

        # Labels for combo boxes/drop-down menus & book price
        self.lab1 = ttk.Label(tab2)
        self.lab1.grid(column=1, row=2)
        self.lab1['text'] = "Category Selection:"

        self.lab2 = ttk.Label(tab2)
        self.lab2.grid(column=7, row=2)
        self.lab2['text'] = "Book Selection:"

        self.lab3 = ttk.Label(tab2)
        self.lab3.grid(column=7, row=1)
        self.lab3['text'] = "Price:"

        # Comboboxes -- drop-down menu implementation of tkinter
        self.com1 = ttk.Combobox(tab2, width=40, state="readonly")
        self.com1.grid(column=1, row=3)
        self.categoryList = inventoryDAO().getCategories()
        print("Category List:\n", self.categoryList)
        self.com1['values'] = self.categoryList
        self.com1.current(0)
        # .bind finds author selected & gets associated book info:
        # when the combobox changes (i.e. event occurs), the callback function is executed
        self.com1.bind("<<ComboboxSelected>>", self.getBooks)  # .bind(event, action)

        self.com2 = ttk.Combobox(tab2, width=40, state="readonly")
        self.com2.grid(column=7, row=3)
        self.bookList = self.DAO.getCategoricalBooks()  # retrieve new books
        tempList = list()
        [tempList.append(book[0]) for book in self.bookList]  # extract book titles, for list, from (title, code, price)
        print(self.bookList)
        self.com2['values'] = tempList
        self.com2.current(0)
        self.com2.bind("<<ComboboxSelected>>", self.getTree)

        # Price display label
        self.lab4 = ttk.Label(tab2, font=("Time New Roman", 20))
        self.lab4.grid(column=8, row=1)
        self.lab4['text'] = f"$ {float(self.bookList[0][2]):.2f}"  # autofill 1st book's price

        # Treeview - an embedded table w/in main frame
        self.tree1 = ttk.Treeview(tab2, columns=('BranchName', 'OnHand'), show='headings')
        self.tree1.heading('BranchName', text='Branch Name')
        self.tree1.heading('OnHand', text='Copies Available')
        self.tree1.grid(column=1, row=1)
        # Fill Treeview w/ values
        self.branchList = self.DAO.getBranchData(bookCode='0378')  # retrieve branch info for default book value
        for row in self.branchList:  # autofill Tree w/ branch inventory info from 1st book
            self.tree1.insert("", "end", values=[row[0], row[1]])

    def getBooks(self, event):
        """For use with author combobox --
        This function is called when a selection is made in the author combo box in order to populate the book combobox,
        tree and price labels.
        As an item is selected from the dropdown it will print in the output window of the IDE for reference/testing.
        Note: selection of an item from the dropdown is considered an 'event' hence the reactionary function argument.
        """
        self.catIndex = event.widget.current()  # this provides the current list index/selection for the category list
        bookCategory = self.categoryList[self.catIndex]  # convert from index location to category type
        print("Category selected is: " + str(bookCategory))

        self.bookList = self.DAO.getCategoricalBooks(category=bookCategory)  # retrieve new books

        for i in self.tree1.get_children():  # When new category is picked -- remove old values in tree list
            self.tree1.delete(i)

        print("\tBooks:", self.bookList)  # print out book list for debugging/tracking/etc
        tempList = list()
        [tempList.append(book[0]) for book in self.bookList]  # extract book title from (title, book_code, price)
        self.com2['values'] = tempList                          # pass title list to combobox
        self.com2.current(0)                        # make book in location 0 by default the auto-filling view
        self.lab4['text'] = f"$ {float(self.bookList[0][2]):.2f}"      # autofill price based of of 1st book, formatted

        # Autofill Treeview w/ 1st book values
        self.branchList = self.DAO.getBranchData(bookCode=self.bookList[0][1])
        print(f"\t---> branch inventory for '{self.bookList[0][0]}':", self.branchList)
        for row in self.branchList:
            self.tree1.insert("", "end", values=[row[0], row[1]])

    def getTree(self, event):
        """For use with book combobox --
        This function is called when a selection is made in the author combo box in order to populate the tree and
        price labels.
        As an item is selected from the dropdown it will print in the output window of the IDE for reference/testing.
        Note: selection of an item from the dropdown is considered an 'event' hence the reactionary function argument.
        """
        for i in self.tree1.get_children():  # Remove old values in tree
            self.tree1.delete(i)

        self.bookIndex = event.widget.current()  # get current book index
        bookCode = self.bookList[self.bookIndex]  # translate index into a book code
        print(
            f"""\tBook Index selected is {self.bookIndex}, Book Code is {bookCode[1]}, price is ${float(bookCode[2]):.2f}""")

        self.branchList = self.DAO.getBranchData(bookCode=bookCode[1])  # retrieve branch info for Tree
        print('\t---> branch holdings:', self.branchList)
        self.lab4['text'] = f"$ {float(bookCode[2]):.2f}"  # update price

        # Fill Treeview w/ values
        for row in self.branchList:
            self.tree1.insert("", "end", values=[row[0], row[1]])


class SBP:
    """Class representing Search by Publisher tab of GUI.
         Takes respective tkinter tab and DAO as arguments
         and then places content onto this particular tab."""
    def __init__(self, tab3, DAO):
        self.getBooks, self.getTree
        self.branchList = 0
        self.DAO = DAO

        # Labels for combo boxes/drop-down menus & book price
        self.lab1 = ttk.Label(tab3)
        self.lab1.grid(column=1, row=2)
        self.lab1['text'] = "Publisher Selection:"

        self.lab2 = ttk.Label(tab3)
        self.lab2.grid(column=7, row=2)
        self.lab2['text'] = "Book Selection:"

        self.lab3 = ttk.Label(tab3)
        self.lab3.grid(column=7, row=1)
        self.lab3['text'] = "Price:"

        # Comboboxes -- drop-down menu implementation of tkinter
        self.com1 = ttk.Combobox(tab3, width=40, state="readonly")
        self.com1.grid(column=1, row=3)
        self.publisherList = inventoryDAO().getPublishers()
        print("Publisher List:\n", self.publisherList)
        self.com1['values'] = self.publisherList
        self.com1.current(0)
        # .bind finds author selected & gets associated book info:
        # when the combobox changes (i.e. event occurs), the callback function is executed
        self.com1.bind("<<ComboboxSelected>>", self.getBooks)  # .bind(event, action)

        self.com2 = ttk.Combobox(tab3, width=40, state="readonly")
        self.com2.grid(column=7, row=3)
        self.bookList = self.DAO.getPublisherBooks()  # retrieve new books
        tempList = list()
        [tempList.append(book[0]) for book in self.bookList]  # extract book titles, for list, from (title, code, price)
        print(self.bookList)
        self.com2['values'] = tempList
        self.com2.current(0)
        self.com2.bind("<<ComboboxSelected>>", self.getTree)

        # Price display label
        self.lab4 = ttk.Label(tab3, font=("Time New Roman", 20))
        self.lab4.grid(column=8, row=1)
        self.lab4['text'] = f"$ {float(self.bookList[0][2]):.2f}"  # autofill 1st book's price

        # Treeview - an embedded table w/in main frame
        self.tree1 = ttk.Treeview(tab3, columns=('BranchName', 'OnHand'), show='headings')
        self.tree1.heading('BranchName', text='Branch Name')
        self.tree1.heading('OnHand', text='Copies Available')
        self.tree1.grid(column=1, row=1)
        # Fill Treeview w/ values
        self.branchList = self.DAO.getBranchData(bookCode='3906')  # retrieve branch info for default book value
        for row in self.branchList:  # autofill Tree w/ branch inventory info from 1st book
            self.tree1.insert("", "end", values=[row[0], row[1]])

    def getBooks(self, event):
        """For use with author combobox --
        This function is called when a selection is made in the author combo box in order to populate the book combobox,
        tree and price labels.
        As an item is selected from the dropdown it will print in the output window of the IDE for reference/testing.
        Note: selection of an item from the dropdown is considered an 'event' hence the reactionary function argument.
        """
        self.pubIndex = event.widget.current()  # this provides the current list index/selection for the category list
        publisher = self.publisherList[self.pubIndex]               # convert from index location to category type
        print("Category selected is: " + str(publisher))

        self.bookList = self.DAO.getPublisherBooks(publisher=publisher)                         # retrieve new books

        for i in self.tree1.get_children():         # When new category is picked -- remove old values in tree list
            self.tree1.delete(i)

        print("\tBooks:", self.bookList)                            # print out book list for debugging/tracking/etc
        tempList = list()
        [tempList.append(book[0]) for book in self.bookList]  # extract book title from (title, book_code, price, publisher)
        self.com2['values'] = tempList                                          # pass title list to combobox
        self.com2.current(0)                                # make book in location 0 by default the auto-filling view
        self.lab4['text'] = f"$ {float(self.bookList[0][2]):.2f}"  # autofill price based of 1st book, formatted

        # Autofill Treeview w/ 1st book values
        self.branchList = self.DAO.getBranchData(bookCode=self.bookList[0][1])
        print(f"\t---> branch inventory for '{self.bookList[0][0]}':", self.branchList)
        for row in self.branchList:
            self.tree1.insert("", "end", values=[row[0], row[1]])

    def getTree(self, event):
        """For use with book combobox --
        This function is called when a selection is made in the author combo box in order to populate the tree and
        price labels.
        As an item is selected from the dropdown it will print in the output window of the IDE for reference/testing.
        Note: selection of an item from the dropdown is considered an 'event' hence the reactionary function argument.
        """
        for i in self.tree1.get_children():                                                 # Remove old values in tree
            self.tree1.delete(i)

        self.bookIndex = event.widget.current()                                               # get current book index
        bookCode = self.bookList[self.bookIndex]                                    # translate index into a book code
        print(
            f"""\tBook Index selected is {self.bookIndex}, Book Code is {bookCode[1]}, price is ${float(bookCode[2]):.2f}""")

        self.branchList = self.DAO.getBranchData(bookCode=bookCode[1])              # retrieve branch info for Tree
        print('\t---> branch holdings:', self.branchList)
        self.lab4['text'] = f"$ {float(bookCode[2]):.2f}"                                           # update price

        # Fill Treeview w/ values
        for row in self.branchList:
            self.tree1.insert("", "end", values=[row[0], row[1]])


if __name__ == '__main__':
    GUI = createGUI()          # start GUI
    GUI.inventoryDAO.close()       # ensure database connection is closed when program ends


