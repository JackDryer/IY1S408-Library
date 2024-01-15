import sqlite3
from helpers import callable_dict
import pprint
import tkinter as  tk
caller = callable_dict()

class CommandCanceled (Exception):
    pass

def exitable_input(prompt):
    result = input(prompt)
    if result.lower() =="quit":
        raise CommandCanceled()
    return result
class UserInterface:
    def __init__(self) -> None:
        self.database = DataBase()
        #self.commands = {"add_book":self.database.add_book, "update_quantity":self.database.update_quantity, "delete": self.database.delete, "update_description":self.database.update_description,"check_status":self.database.check_status, "read":self.database.read}
    def parse(self,raw_command:str):
        "parses a string into a command and its arguments, if an error is through returns 'error' and command and the message in args"
        command_sections = raw_command.split()
        if len(command_sections) == 0:
            return "error", "please enter a command"
        if command_sections[0] not in caller.cmds.keys():
            return "error", "not recognised command"
        if command_sections[0].lower() == "add_author":
            command_sections = command_sections[0], " ".join(command_sections[1:])
        if command_sections[0].lower() == "update_description":
            if len(command_sections) < 4:
                return "error", "not enough arguments"
            command_sections = command_sections[0], command_sections[1], command_sections[2], " ".join(command_sections[3:])
        if command_sections[0].lower() == "add_filter":
            if len(command_sections) < 2:
                return "error", "not enough arguments"
            command_sections = command_sections[0], command_sections[1], " ".join(command_sections[2:])
        if command_sections[0].lower() == "remove_filter":
            if len(command_sections) < 2:
                return "error", "not enough arguments"
        if command_sections[0].lower() == "remove_ordering":
            if len(command_sections) < 2:
                return "error", "not enough arguments"
            command_sections[1] = int(command_sections[1])
        return command_sections[0], command_sections[1:]
    def mainloop(self):
        while True:
            user_input = input("Command: ")
            if user_input.lower()== "quit":
                break
            command, args = self.parse(user_input)
            if command == "error":
                print (args)
            else:
                try:
                    if (x := caller.cmds[command](self.database,*args)) is not None:
                        if isinstance(x,list):
                            pprint.pprint(x)
                        else:
                            print (x)
                    else:
                        print ("Command competed successfully")
                except Exception as e:
                    print (e)
    @caller.add()
    def add_book(self):
        book = {}
        print("adding book, type quit to cancel")
        book["name"] = exitable_input ("Name :")
        book["ISBN_num"] = exitable_input("ISBN_number(leave blank if there is none) :") or None
        book["date"] = exitable_input("Date :")
        book["description"] = exitable_input("Description :")
        book["author_ID"] = exitable_input("author_ID :")
        self.add_book(book)

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        inputbar = tk.Entry(self.root)
        
class DataBase:
    def __init__(self) -> None:
        self.con = sqlite3.connect("database.db")
        self.con.execute("PRAGMA foreign_keys = ON")
        self.cur = self.con.cursor()
        self.filters = []
        self.orderings = []
    
    def add_book (self,book): # not added to caller as the user cant pass in dicts
        #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
        self.cur.execute("INSERT INTO books (name,ISBN_num,date,description,author_ID) VALUES(:name, :ISBN_num,:date,:description,:author_ID)",book)
        self.con.commit()
    @caller.add()
    def help(self):
        pprint.pprint(caller.cmds.keys())
    @caller.add()
    def add_author (self,author_name):
        self.cur.execute("INSERT INTO authors (author_name) VALUES(?)",(author_name,))
        self.con.commit()
        return f"Author added with id {self.cur.lastrowid}"
    @caller.add(alias = "update_quantity")
    def update_stock(self, book_ID, quantity):
        self.cur.execute("DELETE FROM stock WHERE book_ID = ?", (book_ID,))
        self.cur.execute("INSERT INTO stock (book_ID, quantity) VALUES (?, ?)",(book_ID,quantity))
        self.con.commit()
    @caller.add()
    def delete_author (self,author_ID):
        self.cur.execute("DELETE FROM authors WHERE author_ID = ?", (author_ID,))
        self.con.commit()
    @caller.add()
    def delete_book (self,book_ID):
        self.cur.execute("DELETE FROM books WHERE book_ID = ?", (book_ID,))
        self.con.commit()
    @caller.add()
    def update_description(self,book_ID,column,new_description):
        if column not in {"name","ISBN_num","date","description","author_ID"}:# this counts as sqlinjection safe i guess
            return "Please enter a valid column name" 
        self.cur.execute(f"UPDATE books SET {column} = ? WHERE book_ID = ?",(new_description,book_ID))
        self.con.commit()
    @caller.add(alias = "show_status")
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
    @caller.add(alias = "show")
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
    @caller.add()
    def add_filter(self,filter,value):
        if filter in {"book_ID","name","ISBN_num","date","description","author_ID"}:# this counts as sqlinjection safe i guess
            filter = "books."+filter
        elif filter in {"author_name"}:
            filter = "authors."+filter
        else:
            return "Please enter a valid column name"
        self.filters.append((filter,value))
    @caller.add()
    def remove_filter(self,index):
        self.filters.pop(index)
    @caller.add()
    def add_ordering(self,column,direction = "asc"):
        if column in {"book_ID","name","ISBN_num","date","description","author_ID"}:# this counts as sqlinjection safe i guess
            column = "books."+column
        elif column in {"author_name"}:
            column = "authors."+column
        elif column in {"quantity"}:
            column = "stock."+column
        else:
            return "Please enter a valid column name"
        if direction.lower() not in {"asc", "desc"}:
            return "Please enter a valid sorting system" 
        self.orderings.append (column + " " +direction)
    @caller.add()
    def remove_ordering(self,index):
        self.orderings.pop(index)
    @caller.add()
    def show_authors(self):
        self.cur.execute("SELECT * FROM authors")
        return self.cur.fetchall()
    def generate_filters(self):
        filters = " AND ".join((f"{i[0]} = ?" for i in self.filters))
        return " WHERE " + filters if filters else "" , [i[1] for i in self.filters]
    def generate_orderings(self):
        filters = ", ".join(self.orderings)
        return " ORDER BY " + filters if filters else ""
    @caller.add()
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
if __name__ == "__main__":
    #d = DataBase()
    #d.create_database()
    UserInterface().mainloop()
