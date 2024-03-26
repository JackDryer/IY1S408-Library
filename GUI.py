import database_interface
import tkinter as  tk
import re # used to validate user input

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
error_colour_scheme = {
    "bg": "#a10202",
    "fg":"#000000",
    "highlightbackground":"#ff9500",
    "highlightcolor" :"#000000",
}

def configure_colours(element,colour_scheme):
    if isinstance(element,tk.Label):
        new_colour_scheme = colour_scheme.copy()
        if "insertbackground" in colour_scheme:
            new_colour_scheme.pop("insertbackground")
        element.config(activebackground=colour_scheme["highlightbackground"],highlightthickness=0,pady=0,**new_colour_scheme)
        new_colour_scheme.pop("highlightbackground")
        new_colour_scheme.pop("highlightcolor")
    elif isinstance(element,(tk.OptionMenu)): # im sad
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
        self.database = database_interface.DataBase()
        self.root = tk.Tk()
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(1,weight=1)
        self.options = UserOptions(self.root,self.database,self.update_output)
        self.outputbox = BookList(self.root,self.database)
        Book.database =self.database
        self.update_output()
        self.root.mainloop()
    def update_output(self):
        self.outputbox.set_output(self.database.read())

class BetterOptionMenu:
    def __init__(self,master,options:tuple) -> None:
        self.strvar = tk.StringVar(value=options[0])
        self.box = tk.OptionMenu(master,self.strvar,*options)
        configure_colours(self.box,colour_scheme=colour_scheme)
class ColumnOption (BetterOptionMenu):
    def __init__(self, master) -> None:
        super().__init__(master, (database_interface.BOOKS_FIELDS[0],)+Book.book_fields+(Book.author_feild,Book.stock_field))
        
class UserOptions:
    def __init__(self,root,database:database_interface.DataBase, update_func : callable) -> None:
        self.database = database
        self.update_output = update_func
        # set up frame object
        frame = tk.Frame(root)
        frame.grid_rowconfigure(1,weight=1)
        frame.grid_columnconfigure(1,weight=1)
        frame.grid(sticky="NSEW")
        # setting up options
        self.filter_field = ColumnOption(frame)
        self.filter_str = tk.StringVar()
        self.filter = tk.Entry(frame,textvariable=self.filter_str)
        configure_colours(self.filter,colour_scheme=colour_scheme)
        self.sorting = ColumnOption(frame)
        self.sorting_direction = BetterOptionMenu(frame,("asc","desc"))
        # gridding into place
        self.filter_field.box.grid(row = 0, column=0, sticky="NSEW")
        self.filter.grid(row = 0, column= 1, sticky="NSEW")
        self.sorting.box.grid(row = 0, column= 2, sticky="NSEW")
        self.sorting_direction.box.grid(row = 0, column= 3, sticky="NSEW")
        #bindings
        self.sorting.strvar.trace_add("write", self.update_ordering)
        self.sorting_direction.strvar.trace_add("write", self.update_ordering)
        self.database.add_ordering("book_ID")# so that it can be removed later
        self.filter_field.strvar.trace_add("write", self.update_filtering)
        self.filter_str.trace_add("write", self.update_filtering)

    def update_ordering(self,*args):
        self.database.remove_ordering(0)
        self.database.add_ordering(self.sorting.strvar.get(),self.sorting_direction.strvar.get())
        self.update_output()
    def update_filtering(self,*args):
        try:
            re.compile(self.filter_str.get())
            configure_colours(self.filter,colour_scheme)
        except re.error:
            configure_colours(self.filter,error_colour_scheme)
            return
        if self.database.generate_filters()[0]!="":
            self.database.remove_filter(0)
        if self.filter_str.get():
            self.database.add_filter(self.filter_field.strvar.get(),self.filter_str.get())
        self.update_output()
class BookList:
    def __init__(self,master,database):
        self.frame = tk.Frame(master)
        for i in range(6):
            self.frame.columnconfigure(i,weight=1)
        self.create_headings()
        self.frame.grid(row = 1, column= 0,sticky="NSEW")
        self.displayed_books= []
        self.update_func = database
    def create_headings(self):
        for i,name in enumerate(Book.book_fields+(Book.author_feild,Book.stock_field)):
            border = tk.Frame(self.frame,background="black",borderwidth=1)
            border.grid_columnconfigure(0,weight=1)
            label = tk.Label (border,text=name[0].upper()+name[1:])
            configure_colours(label,highlight_colour_scheme)
            label.grid(sticky="NSEW")
            border.grid(row=0,column=i,sticky="NSEW")
    def set_output(self,data):
        self.data = data
        self.update_output()
    def update_output(self):
        self.clear_output()
        length = len(self.data)
        for row, book in enumerate(self.data[:50]):
            self.displayed_books.append(Book(self.frame,row+1,book,self.update_func))
    def clear_output(self):
        for book in self.displayed_books:
            book.destroy()
        self.displayed_books = []
class Book:
    book_fields = database_interface.BOOKS_FIELDS[1:-1]
    author_feild = database_interface.AUTHOR_FIELDS[1]
    stock_field = database_interface.STOCK_FIELDS[1]
    def __init__(self,master:tk.Frame,row,book,databaseObject:database_interface.DataBase):
        self.master = master
        self.row = row
        self.book = book
        self.database = databaseObject
        self.entries= []
        self.ID = book["book_ID"]
        temp = [self.create_element(i) for i in self.book_fields]
        stock = self.create_element(self.stock_field)
        vcmd = (self.master.register(lambda x: x.isdigit() or x ==""))
        stock.configure(validate="all",validatecommand=(vcmd, '%P'))
        self.author = tk.StringVar(master)
        self.author.set(book["author_name"])
        self.author_dictionary = {i[1]:i[0] for i in self.database.show_authors()}
        authorbox = tk.OptionMenu(master,self.author,*self.author_dictionary.keys())
        authorbox.column_name = self.author_feild
        for x, i in enumerate(temp):
            self.config_element(i,x)
        self.config_element(authorbox,x+1)
        self.config_element(stock,x+2)
        self.author.trace_add("write",self.set_author)

    def create_element(self,column_name) ->tk.Entry:
        entry = tk.Entry(self.master)
        entry.insert(tk.END,str(self.book[column_name]))
        entry.column_name = column_name # this is deffinatly not a good idea, should use inheritance, but it doesn't change the funtionality.
        return entry

    def config_element(self,element,column):
        configure_colours(element,colour_scheme)
        element.grid(row=self.row,column=column,sticky="NSEW")
        element.bind("<FocusOut>",lambda x: self.leave_entry(element))
        element.bind("<FocusIn>", lambda x: self.enter_entry(element))
        self.entries.append(element)
    
    def leave_entry(self,entry:tk.Entry):
        for i in self.entries:
            configure_colours(i,colour_scheme)
        if entry.column_name == self.author_feild:
            pass
        elif entry.column_name ==self.stock_field:
            self.database.update_stock(self.ID,int(entry.get()))
        else:
            self.database.update_description(self.ID,entry.column_name,entry.get())
    def enter_entry(self,entry):
        for i in self.entries:
            configure_colours(i,highlight_colour_scheme)
            entry.configure(**select_colour_scheme)
    def set_author(self,irreleventvalue,irreleventvalue2,irreleventvalue3):
        self.database.update_description(self.ID,"author_ID",self.author_dictionary[self.author.get()])
    def destroy(self):
        for i in self.entries:
            i.destroy()

if __name__ == "__main__":
    #d = DataBase()
    #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
    #for i in range (10000,20000):
    #     d.delete_book(i)
        #d.add_book(book)
    #d.commit()
    ui =UserInterface()

