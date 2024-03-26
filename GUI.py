import database_interface
import tkinter as  tk
import re # used to validate user input
from tkinter import messagebox
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
    if isinstance(element,(tk.Label,tk.Button)):
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
        self.root.rowconfigure(2,weight=1)
        self.active_book = BookHolder() # i want rusts option type but alas this is python
        self.options = UserOptions(self.root,self.database,self.update_output)
        self.menu = Menu(self.root,self.database,self.update_output,self.active_book)
        self.outputbox = BookList(self.root,self.database,self.active_book)
        Book.database =self.database
        self.update_output()
        self.root.mainloop()
    def update_output(self):
        self.outputbox.set_output(self.database.read())
class BookHolder:
    def __init__(self) -> None:
        self.book :Book = None
class Menu:
    def __init__(self,root,database:database_interface.DataBase,update_function, active_book:BookHolder) -> None:
        self.database = database
        self.active_book = active_book
        self.update_output =update_function
        self.frame = tk.Frame(root,background=colour_scheme["bg"])
        self.frame.grid_rowconfigure(0,weight=1)
        #self.frame.grid_columnconfigure(0,weight=1)
        self.frame.grid(sticky="NSEW")
        self.add_book_button = tk.Button(self.frame,text="add book")
        configure_colours(self.add_book_button,colour_scheme)
        self.add_book_button.grid(sticky="NSEW")
        self.delete_book_button = tk.Button(self.frame,text="delete book",command=self.confirm_delete_book)
        configure_colours(self.delete_book_button,colour_scheme)
        self.delete_book_button.grid(row= 0, column=1, sticky="NSEW")
    def confirm_delete_book(self):
        if self.active_book.book ==None:         
            messagebox.showwarning(title="",message="You must select a book before you can delete it")
        else:
            popup = tk.Toplevel(self.frame)
            for i in range(6):
                popup.columnconfigure(i,weight=1)
            are_you_sure = tk.Label(popup,text= "Are you sure you want to delete this book?",font=("Arial", 14))
            configure_colours(are_you_sure,colour_scheme)
            are_you_sure.grid(sticky="NSEW",columnspan=6)
            add_headings(popup,1)
            diplayed_book = Book(popup,2,self.active_book.book.book_dict,self.database,BookHolder())
            options = tk.Frame(popup,bg = colour_scheme["bg"])
            options.grid(sticky="NSEW",columnspan=6)
            for column, weight in enumerate((5,1,1,1,5)):
                options.grid_columnconfigure(column,weight=weight)
            no_button = tk.Button(options,text="No",command= popup.destroy)
            configure_colours(no_button,colour_scheme)
            no_button.grid(row=0,column=1,sticky="NSEW")
            no_button.focus()
            yes_button = tk.Button(options,text="yes",command= lambda book = self.active_book.book :self.delete_book(book,popup)) # contain the book so this popup is always associated with this book
            configure_colours(yes_button,colour_scheme)
            yes_button.grid(row=0,column=3,sticky="NSEW")
            popup.bind('<Return>',lambda e:no_button.invoke()) # dont delete my befult
    def delete_book(self,book,popup:tk.Toplevel):
        self.database.delete_book(book.ID)
        popup.destroy()
        self.update_output()

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
        self.frame = tk.Frame(root)
        self.frame.grid_rowconfigure(1,weight=1)
        self.frame.grid_columnconfigure(1,weight=1)
        self.frame.grid(sticky="NSEW")
        # setting up options
        self.filter_field = ColumnOption(self.frame)
        self.filter_str = tk.StringVar()
        self.filter = tk.Entry(self.frame,textvariable=self.filter_str)
        configure_colours(self.filter,colour_scheme=colour_scheme)
        self.sorting = ColumnOption(self.frame)
        self.sorting_direction = BetterOptionMenu(self.frame,("asc","desc"))
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
def add_headings(frame, row = 0) -> None:
    for i,name in enumerate(Book.book_fields+(Book.author_feild,Book.stock_field)):
        border = tk.Frame(frame,background="black",borderwidth=1)
        border.grid_columnconfigure(0,weight=1)
        label = tk.Label (border,text=name[0].upper()+name[1:])
        configure_colours(label,highlight_colour_scheme)
        label.grid(sticky="NSEW")
        border.grid(row=row,column=i,sticky="NSEW")
class BookList:
    def __init__(self,master,database,active_book):
        self.frame = tk.Frame(master)
        self.active_book = active_book
        for i in range(6):
            self.frame.columnconfigure(i,weight=1)
        add_headings(self.frame)
        self.frame.grid(row = 2, column= 0,sticky="NSEW")
        self.displayed_books= []
        self.update_func = database
    def set_output(self,data):
        self.data = data
        self.update_output()
    def update_output(self):
        self.clear_output()
        length = len(self.data)
        for row, book_dict in enumerate(self.data[:50]):
            self.displayed_books.append(Book(self.frame,row+1,book_dict,self.update_func,self.active_book))
    def clear_output(self):
        for book in self.displayed_books:
            book.destroy()
        self.displayed_books = []
class Book:
    book_fields = database_interface.BOOKS_FIELDS[1:-1]
    author_feild = database_interface.AUTHOR_FIELDS[1]
    stock_field = database_interface.STOCK_FIELDS[1]
    def __init__(self,master:tk.Frame,row,book_dict,databaseObject:database_interface.DataBase,active_book):
        self.master = master
        self.row = row
        self.book_dict = book_dict
        self.database = databaseObject
        self.active_book = active_book
        self.entries= []
        self.ID = book_dict["book_ID"]
        temp = [self.create_element(i) for i in self.book_fields]
        stock = self.create_element(self.stock_field)
        vcmd = (self.master.register(lambda x: x.isdigit() or x ==""))
        stock.configure(validate="all",validatecommand=(vcmd, '%P'))
        self.author = tk.StringVar(master)
        self.author.set(book_dict["author_name"])
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
        entry.insert(tk.END,str(self.book_dict[column_name]))
        entry.column_name = column_name # this is deffinatly not a good idea, should use inheritance, but it doesn't change the funtionality.
        return entry

    def config_element(self,element,column):
        configure_colours(element,colour_scheme)
        element.grid(row=self.row,column=column,sticky="NSEW")
        element.bind("<FocusOut>",lambda x: self.leave_entry(element))
        element.bind("<FocusIn>", lambda x: self.enter_entry(element))
        self.entries.append(element)
    
    def leave_entry(self,entry:tk.Entry):
        self.active_book.book = None 
        for i in self.entries:
            configure_colours(i,colour_scheme)
        if entry.column_name == self.author_feild:
            return
        elif entry.column_name ==self.stock_field:
            self.database.update_stock(self.ID,int(entry.get()))
        else:
            self.database.update_description(self.ID,entry.column_name,entry.get())
        self.book_dict[entry.column_name] = entry.get()
    def enter_entry(self,entry):
        self.active_book.book = self
        for i in self.entries:
            configure_colours(i,highlight_colour_scheme)
            entry.configure(**select_colour_scheme)
    def set_author(self,irreleventvalue,irreleventvalue2,irreleventvalue3):
        self.book_dict["author_name"] =self.author.get()
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

