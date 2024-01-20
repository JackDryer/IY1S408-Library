import sqlite3        

class DataBase:
    def __init__(self) -> None:
        self.con = sqlite3.connect("database.db")
        self.con.execute("PRAGMA foreign_keys = ON")
        self.cur = self.con.cursor()
        self.filters = []
        self.orderings = []
    
    def add_book (self,book): # not added to caller as the user cant pass in dicts
        #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","de
        # scription":"it exists","author_ID":1}
        self.cur.execute("INSERT INTO books (name,ISBN_num,date,description,author_ID) VALUES(:name, :ISBN_num,:date,:description,:author_ID)",book)

    def add_author (self,author_name):
        self.cur.execute("INSERT INTO authors (author_name) VALUES(?)",(author_name,))
        self.con.commit()
        return f"Author added with id {self.cur.lastrowid}"
    def update_author(self,author_ID:int,author_name:str):
        self.cur.execute(f"UPDATE authors SET author_name = ? WHERE book_ID = ?",(author_name,author_ID))
        self.con.commit()
    def update_stock(self, book_ID, quantity):
        self.cur.execute("DELETE FROM stock WHERE book_ID = ?", (book_ID,))
        self.cur.execute("INSERT INTO stock (book_ID, quantity) VALUES (?, ?)",(book_ID,quantity))
        self.con.commit()
    def delete_author (self,author_ID):
        self.cur.execute("DELETE FROM authors WHERE author_ID = ?", (author_ID,))
        self.con.commit()

    def delete_book (self,book_ID):
        self.cur.execute("DELETE FROM books WHERE book_ID = ?", (book_ID,))
    def commit(self):
        self.con.commit()

    def update_description(self,book_ID:int,column:str,new_description:str):
        if column not in {"name","ISBN_num","date","description","author_ID"}:# this counts as sqlinjection safe i guess
            raise Exception( "Please enter a valid column name") 
        self.cur.execute(f"UPDATE books SET {column} = ? WHERE book_ID = ?",(new_description,book_ID))
        self.con.commit()

    def check_status(self):
        filtersql,values = self.generate_filters()
        self.cur.execute(f"""SELECT books.name,
    COALESCE (stock.quantity, 0) AS quantity 
FROM books LEFT OUTER JOIN stock  
ON books.book_ID = stock.book_ID
{filtersql} {self.generate_orderings()}""",values)

        result_lists =self.cur.fetchall()
        results = [
            {
                row[0]: "In Stock" if row[1]>0 else "Out of Stock"
            }
            for row in result_lists
        ]
        return results

    def read(self):
        #self.cur.execute("SELECT * FROM authors")
        filtersql,values = self.generate_filters()
        
        self.cur.execute(f"""SELECT books.*,
COALESCE (stock.quantity, 0) AS quantity, authors.author_name
FROM books LEFT OUTER JOIN stock  
ON books.book_ID = stock.book_ID
JOIN authors ON books.author_ID = authors.author_ID
{filtersql} {self.generate_orderings()}""",values)
        result_lists =self.cur.fetchall()
        results = [
            { 
                i: row[x] 
                for x, i in enumerate(("book_ID","name","ISBN_num","date","description","author_ID","quantity","author_name"))
            }
            for row in result_lists
            ]
        return results

    def add_filter(self,filter,value):
        if filter in {"book_ID","name","ISBN_num","date","description","author_ID"}:# this counts as sqlinjection safe i guess
            filter = "books."+filter
        elif filter in {"author_name"}:
            filter = "authors."+filter
        else:
            raise Exception("Please enter a valid column name")
        self.filters.append((filter,value))

    def remove_filter(self,index):
        self.filters.pop(index)

    def add_ordering(self,column,direction = "asc"):
        if column in {"book_ID","name","ISBN_num","date","description","author_ID"}:# this counts as sqlinjection safe i guess
            column = "books."+column
        elif column in {"author_name"}:
            column = "authors."+column
        elif column in {"quantity"}:
            column = "stock."+column
        else:
            raise Exception( "Please enter a valid column name")
        if direction.lower() not in {"asc", "desc"}:
            raise Exception("Please enter a valid sorting system") 
        self.orderings.append (column + " " +direction)

    def remove_ordering(self,index):
        self.orderings.pop(index)

    def show_authors(self):
        self.cur.execute("SELECT * FROM authors")
        return self.cur.fetchall()
    def generate_filters(self):
        filters = " AND ".join((f"{i[0]} = ?" for i in self.filters))
        return " WHERE " + filters if filters else "" , [i[1] for i in self.filters]
    def generate_orderings(self):
        filters = ", ".join(self.orderings)
        return " ORDER BY " + filters if filters else ""

    def create_database(self):
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

