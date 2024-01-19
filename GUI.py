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
        self.outputbox = BookList(self.root)
        self.outputbox.set_output(self.database.read())
        Book.database =self.database
        self.root.mainloop()

class BookList:
    def __init__(self,master):
        self.frame = tk.Frame(master)
        self.frame.grid(sticky="NSEW")
        self.displayed_books= []
    def set_output(self,data):
        self.data = data
        self.update_output()
    def update_output(self):
        lenght = len(self.data)
        for row, book in enumerate(self.data):
            self.displayed_books.append(Book(self.frame,row,book))
            
class Book:
    def __init__(self,master,row,book):
        self.master = master
        self.ID = book["book_ID"]
        entry = tk.Entry(self.master,**colour_scheme)
        entry.grid(row=row,column=1)
        entry.insert(tk.END,str(book["name"]))
        entry.bind("<FocusOut>",lambda x: self.leave_entry(entry))
        entry.bind("<FocusIn>", lambda x: entry.configure(**highlight_colour_scheme))
    def add_element(self,column,value):
        pass
    def leave_entry(self,entry:tk.Entry):
        entry.configure(**colour_scheme)
        ui.database.update_description(self.ID,)



if __name__ == "__main__":
    #d = DataBase()
    #book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
    #for i in range (10000,20000):
    #     d.delete_book(i)
        #d.add_book(book)
    #d.commit()
    ui =UserInterface()