import database
import tkinter as  tk
colour_scheme = {
    "bg": "#010740",
    "fg":"#ffffff",
    "insertbackground": "#ffffff",
    "highlightcolor" :"#000000",
    "highlightbackground":"#ff9500",
}
highlight_colour_scheme ={
    "bg":"#8c98ff",
    "fg":"#000000",
    "highlightbackground":"#ff9500",
    "highlightcolor" :"#000000",
}

select_colour_scheme = {
    "bg": "#ff9500",
    "fg":"#000000",
    "highlightbackground":"#ff9500",
    "highlightcolor" :"#000000",
}

def configure_colours(element,colour_scheme):
    if isinstance(element,tk.OptionMenu): # im sad
        new_colour_scheme = colour_scheme.copy()
        if "insertbackground" in colour_scheme:
            new_colour_scheme.pop("insertbackground")
        element.config(activebackground=colour_scheme["highlightbackground"],highlightthickness=0,pady=0,**new_colour_scheme)
        new_colour_scheme.pop("highlightbackground")
        new_colour_scheme.pop("highlightcolor")
        element["menu"].config(activebackground=colour_scheme["highlightbackground"],activeforeground=colour_scheme["highlightcolor"],borderwidth=0,activeborderwidth = 0,**new_colour_scheme)
    else:
        element.config(**colour_scheme)

class UserInterface:
    def __init__(self) -> None:
        self.database = database.DataBase()
        self.root = tk.Tk()
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.outputbox = BookList(self.root,self.database)
        self.outputbox.set_output(self.database.read())
        Book.database =self.database
        self.root.mainloop()

class BookList:
    def __init__(self,master,database):
        self.frame = tk.Frame(master)
        self.frame.grid(sticky="NSEW")
        self.displayed_books= []
        self.update_func = database
    def set_output(self,data):
        self.data = data
        self.update_output()
    def update_output(self):
        lenght = len(self.data)
        for row, book in enumerate(self.data):
            self.displayed_books.append(Book(self.frame,row,book,self.update_func))
            
class Book:
    book_fields = database.BOOKS_FIELDS[1:-1]
    author_feild = database.AUTHOR_FIELDS[1]
    stock_field = database.STOCK_FIELDS[1]
    def __init__(self,master,row,book,databaseObject):
        self.master = master
        self.row = row
        self.book = book
        self.database = databaseObject
        self.entries= []
        self.ID = book["book_ID"]
        for x, i in enumerate(self.book_fields + (self.stock_field,)):
            self.add_element(x,i)
        author = tk.StringVar(master)
        author.set(book["author_name"])
        authorbox = tk.OptionMenu(master,author,*[i[1] for i in self.database.show_authors()])
        configure_colours(authorbox,colour_scheme)
        self.entries.append(authorbox)
        authorbox.grid(row=row,column=x+1,sticky= "NSEW")

    def add_element(self,column,column_name):
        entry = tk.Entry(self.master,**colour_scheme)
        entry.grid(row=self.row,column=column,sticky="NSEW")
        entry.insert(tk.END,str(self.book[column_name]))
        entry.column_name = column_name # this is deffinatly not a good idea, should use inheritance, but it doesn't change the funtionality.
        entry.bind("<FocusOut>",lambda x: self.leave_entry(entry))
        entry.bind("<FocusIn>", lambda x: self.enter_entry(entry))
        self.entries.append(entry)
    def leave_entry(self,entry:tk.Entry):
        for i in self.entries:
            configure_colours(i,colour_scheme)
        self.database.update_description(self.ID,entry.column_name,entry.get())
    def enter_entry(self,entry):
        for i in self.entries:
            configure_colours(i,highlight_colour_scheme)
        entry.configure(**select_colour_scheme)


if __name__ == "__main__":
    #d = DataBase()
    #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
    #for i in range (10000,20000):
    #     d.delete_book(i)
        #d.add_book(book)
    #d.commit()
    ui =UserInterface()