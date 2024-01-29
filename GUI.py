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
    def __init__(self,master:tk.Frame,row,book,databaseObject:database.DataBase):
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
        self.config_element(stock,x+1)
        self.config_element(authorbox,x+2)
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


if __name__ == "__main__":
    #d = DataBase()
    #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
    #for i in range (10000,20000):
    #     d.delete_book(i)
        #d.add_book(book)
    #d.commit()
    ui =UserInterface()