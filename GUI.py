from database import DataBase
import tkinter as  tk
colour_scheme = {
    "bg": "#010740",
    "fg":"#ffffff",
    "insertbackground": "#ffffff",
    "highlightcolor" :"#ff9500",
    "highlightbackground":"#000000",
}
highlight_colour_scheme = {
    "bg": "#ff9500",
    "fg":"#000000",
}

class UserInterface:
    def __init__(self) -> None:
        self.database = DataBase()
        self.root = tk.Tk()
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.outputbox = BookList(self.root,self.database.update_description)
        self.outputbox.set_output(self.database.read())
        Book.database =self.database
        self.root.mainloop()

class BookList:
    def __init__(self,master,update_func):
        self.frame = tk.Frame(master)
        self.frame.grid(sticky="NSEW")
        self.displayed_books= []
        self.update_func = update_func
    def set_output(self,data):
        self.data = data
        self.update_output()
    def update_output(self):
        lenght = len(self.data)
        for row, book in enumerate(self.data):
            self.displayed_books.append(Book(self.frame,row,book,self.update_func))
            
class Book:
    def __init__(self,master,row,book,update_func):
        self.master = master
        self.row = row
        self.book = book
        self.update_func = update_func
        self.ID = book["book_ID"]
        for x, i in enumerate(["name","ISBN_num","date","description","quantity","author_name"]):
            self.add_element(x,i)

    def add_element(self,column,column_name):
        entry = tk.Entry(self.master,**colour_scheme)
        entry.grid(row=self.row,column=column)
        entry.insert(tk.END,str(self.book[column_name]))
        entry.column_name = column_name # this is deffinatly not a good idea, should use inheritance, but it doesn't change the funtionality.
        entry.bind("<FocusOut>",lambda x: self.leave_entry(entry))
        entry.bind("<FocusIn>", lambda x: entry.configure(**highlight_colour_scheme))
    def leave_entry(self,entry:tk.Entry):
        entry.configure(**colour_scheme)
        self.update_func(self.ID,entry.column_name,entry.get())

        



if __name__ == "__main__":
    #d = DataBase()
    #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
    #for i in range (10000,20000):
    #     d.delete_book(i)
        #d.add_book(book)
    #d.commit()
    ui =UserInterface()