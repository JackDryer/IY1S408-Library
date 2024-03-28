import sqlite3
from typing import Final, Tuple, List, Dict
from enum import Enum
import re


def regexp(expr, item):
    item = str(item)
    reg = re.compile(expr)
    return reg.fullmatch(item) is not None


AUTHOR_TABLE: Final[str] = "authors"
AUTHOR_FIELDS: Final[Tuple[str]] = ("author_ID", "author_name")

BOOKS_TABLE: Final[str] = "books"
BOOKS_FIELDS: Final[Tuple[str]] = (
    "book_ID", "name", "ISBN_num", "date", "description", "author_ID")
BOOK_FIELD: Final[Enum] = Enum("BOOK_FEILD", BOOKS_FIELDS)

STOCK_TABLE: Final[str] = "stock"
STOCK_FIELDS: Final[Tuple[str]] = ("book_ID", "quantity")


class DataBase:
    """Defines an API to interact with the SQL database"""

    def __init__(self) -> None:
        self.con = sqlite3.connect("database.db")
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.create_function("REGEXP", 2, regexp)
        self.cur = self.con.cursor()
        self.filters = []
        self.orderings = []

    def add_book(self, book: Dict[str, str]) -> None:
        """adds a book to the database, adds an associated field in the stock table if it is specified

        Parameters:
            book: a dictionary defining  book to add
        this should have as keys name, ISBN_numb, date, description, and author_ID
        """
        # book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","de
        # scription":"it exists","author_ID":1}
        self.cur.execute(
            "INSERT INTO books (name,ISBN_num,date,description,author_ID) VALUES(:name, :ISBN_num,:date,:description,:author_ID) RETURNING book_ID", book)
        row = self.cur.fetchone()
        (id, ) = row if row else None
        self.con.commit()
        if STOCK_FIELDS[1] in book and (quantity := book[STOCK_FIELDS[1]]) != "":
            self.update_stock(id, quantity)

    def add_author(self, author_name: str) -> None:
        """Adds an author to the authors table

        Parameters:
            author_name: the name of the author to add"""
        self.cur.execute(
            "INSERT INTO authors (author_name) VALUES(?)", (author_name,))
        self.con.commit()
        return f"Author added with id {self.cur.lastrowid}"

    def update_author(self, author_ID: int, author_name: str) -> None:
        """Updates an authors name in the authors table

        Parameters:
            author_ID: the ID of the author to change
            author_name: the new name of the author"""
        self.cur.execute(
            f"UPDATE authors SET author_name = ? WHERE book_ID = ?", (author_name, author_ID))
        self.con.commit()

    def update_stock(self, book_ID: int, quantity: int) -> None:
        """Updates the stock stored of a book

        Parameters:
            bookID: the ID of the book to update
            quantity: the new quantity to set
        """
        self.cur.execute("DELETE FROM stock WHERE book_ID = ?", (book_ID,))
        self.cur.execute(
            "INSERT INTO stock (book_ID, quantity) VALUES (?, ?)", (book_ID, quantity))
        self.con.commit()

    def delete_author(self, author_ID: int) -> None:
        """deletes an author (and all associated books) from the database

        Parameters:
            author_ID: the ID of the author to delete"""
        self.cur.execute(
            "DELETE FROM authors WHERE author_ID = ?", (author_ID,))
        self.con.commit()

    def delete_book(self, book_ID: int) -> None:
        """deletes a book from the database

        Parameters:
            book_ID: the ID of the book to delete"""
        self.cur.execute("DELETE FROM books WHERE book_ID = ?", (book_ID,))
        self.con.commit()

    def update_description(self, book_ID: int, column: str, new_description: str) -> None:
        """updates an aspect of a book

        Parameters:
            book_ID: the ID of the book to modify
            column: the felid to modify
            new_description: the new value"""
        if column not in {"name", "ISBN_num", "date", "description", "author_ID"}:  # this counts as sqlinjection safe i guess
            raise Exception("Please enter a valid column name")
        self.cur.execute(f"UPDATE books SET {
                         column} = ? WHERE book_ID = ?", (new_description, book_ID))
        self.con.commit()

    def check_status(self) -> List[str]:
        """returns the status of all books, In Stock or Out of Stock"""
        filtersql, values = self.generate_filters()
        self.cur.execute(f"""SELECT books.name,
    COALESCE (stock.quantity, 0) AS quantity
FROM books LEFT OUTER JOIN stock
ON books.book_ID = stock.book_ID
{filtersql} {self.generate_orderings()}""", values)

        result_lists = self.cur.fetchall()
        results = [
            {
                row[0]: "In Stock" if row[1] > 0 else "Out of Stock"
            }
            for row in result_lists
        ]
        return results

    def read(self) -> List[Dict[str, str]]:
        """read the database according to the set filters and orderings

        Returns:
            All items in the database
        format is: [{"book_ID" :123, "name": "the books name" ...}...]
        """
        # self.cur.execute("SELECT * FROM authors")
        filtersql, values = self.generate_filters()

        self.cur.execute(f"""SELECT books.*,
COALESCE (stock.quantity, 0) AS quantity, authors.author_name
FROM books LEFT OUTER JOIN stock
ON books.book_ID = stock.book_ID
JOIN authors ON books.author_ID = authors.author_ID
{filtersql} {self.generate_orderings()}""", values)
        result_lists = self.cur.fetchall()
        # compreherions are funny
        results = [
            {
                i: row[x]
                for x, i in enumerate(("book_ID", "name", "ISBN_num", "date", "description", "author_ID", "quantity", "author_name"))
            }
            for row in result_lists
        ]
        return results

    def add_filter(self, filter: str, value: str) -> None:
        """Add a filter to the database

        Parameters:
            filter: the column to filter by
            value: the value to compare to
        """
        if filter in {"book_ID", "name", "ISBN_num", "date", "description", "author_ID"}:  # this counts as sqlinjection safe i guess
            filter = "books."+filter
        elif filter in {"author_name"}:
            filter = "authors."+filter
        else:
            raise Exception("Please enter a valid column name")
        self.filters.append((filter, value))

    def remove_filter(self, index: int) -> None:
        """Remove a filter from the database

        Parameters:
            index: the index of the filter to remove"""
        self.filters.pop(index)

    def add_ordering(self, column: str, direction: str = "asc") -> None:
        """Tell the read function to return in a specific order

        Parameters:
            column: the column to order by
            direction: the direction to order in"""
        # this counts as sqlinjection safe i guess
        if column in {"book_ID", "name", "ISBN_num", "date", "description", "author_ID"}:
            column = "books."+column
        elif column in {"author_name"}:
            column = "authors."+column
        elif column in {"quantity"}:
            column = "stock."+column
        else:
            raise Exception("Please enter a valid column name")
        if direction.lower() not in {"asc", "desc"}:
            raise Exception("Please enter a valid sorting system")
        self.orderings.append(column + " " + direction)

    def remove_ordering(self, index: int) -> None:
        """Remove an ordering from the database

        Parameters:
            index: the index of the ordering to remove"""
        self.orderings.pop(index)

    def get_authors(self) -> Dict[int, str]:
        """returns a dictionary of each author in the database and their ID"""
        self.cur.execute("SELECT * FROM authors")
        return {i[1]: i[0] for i in self.cur.fetchall()}

    def generate_filters(self) -> str:
        """return part of an an sql statement to filter by the set filters"""
        filters = " AND ".join((f"{i[0]} REGEXP ?" for i in self.filters))
        return " WHERE " + filters if filters else "", [i[1] for i in self.filters]

    def generate_orderings(self) -> str:
        """return part of an an sql statement to order by the set orderings"""
        filters = ", ".join(self.orderings)
        return " ORDER BY " + filters if filters else ""

    def create_database(self) -> None:
        """create the necessary tables in the database"""
        self.cur.execute("""CREATE TABLE authors(
  author_ID    INTEGER PRIMARY KEY, 
  author_name  TEXT
)""")
        self.cur.execute("""CREATE TABLE books(
book_ID INTEGER PRIMARY KEY,
name TEXT NOT NULL, 
ISBN_num TEXT,
date,
description TEXT,
author_ID INTEGER NOT NULL,
FOREIGN KEY(author_ID) REFERENCES authors(author_ID) ON DELETE CASCADE
 )""")
        self.cur.execute("""CREATE TABLE stock(
book_ID INTEGER NOT NULL,
quantity INTEGER NOT NULL,
FOREIGN KEY(book_ID) REFERENCES books(book_ID) ON DELETE CASCADE
 )""")
