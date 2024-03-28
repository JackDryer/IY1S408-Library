import database_interface
import tkinter as tk
import re  # used to validate user input
from tkinter import messagebox
from collections.abc import Callable
from typing import Dict, List, Iterable

colour_scheme = {
    "bg": "#010740",
    "fg": "#ffffff",
    "insertbackground": "#ffffff",
    "highlightcolor": "#000000",
    "highlightbackground": "#ff9500",
}
highlight_colour_scheme = {
    "bg": "#8c98ff",
    "fg": "#000000",
    "highlightbackground": "#ff9500",
    "highlightcolor": "#000000",
}

select_colour_scheme = {
    "bg": "#ff9500",
    "fg": "#000000",
    "highlightbackground": "#ff9500",
    "highlightcolor": "#000000",
}
error_colour_scheme = {
    "bg": "#a10202",
    "fg": "#000000",
    "highlightbackground": "#ff9500",
    "highlightcolor": "#000000",
}


def configure_colours(element: tk.Widget, colour_scheme: Dict[str, str]) -> None:
    """Takes a tkinter widget and configures it using the colour scheme

    Parameters:
    element -- tke tkinter element to configure
    colour_scheme -- a dictionary describing the desired colour scheme
    """
    if isinstance(element, (tk.Label, tk.Button)):
        new_colour_scheme = colour_scheme.copy()
        if "insertbackground" in colour_scheme:
            new_colour_scheme.pop("insertbackground")
        element.config(
            activebackground=colour_scheme["highlightbackground"], highlightthickness=0, pady=0, **new_colour_scheme)
        new_colour_scheme.pop("highlightbackground")
        new_colour_scheme.pop("highlightcolor")
    elif isinstance(element, (tk.OptionMenu)):  # im sad
        new_colour_scheme = colour_scheme.copy()
        if "insertbackground" in colour_scheme:
            new_colour_scheme.pop("insertbackground")
        element.config(
            activebackground=colour_scheme["highlightbackground"], highlightthickness=0, pady=0, **new_colour_scheme)
        new_colour_scheme.pop("highlightbackground")
        new_colour_scheme.pop("highlightcolor")
        element["menu"].config(activebackground=colour_scheme["highlightbackground"],
                               activeforeground=colour_scheme["highlightcolor"], borderwidth=0, activeborderwidth=0, **new_colour_scheme)
    else:
        element.config(**colour_scheme)


class UserInterface:
    """Entry point of the program, defines and sets up all necessary components"""

    def __init__(self) -> None:
        self.database = database_interface.DataBase()
        self.root = tk.Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.active_book = BookHolder()  # i want rusts option type but alas this is python
        self.options = UserOptions(
            self.root, self.database, self.update_output)
        self.menu = Menu(self.root, self.database,
                         self.update_output, self.active_book)
        self.outputbox = BookList(self.root, self.database, self.active_book)
        Book.database = self.database
        self.update_output()
        self.root.mainloop()

    def update_output(self) -> None:
        """Update the view of the user interface to match the current state of the database"""
        self.outputbox.set_output(self.database.read())


class BookHolder:
    """holds a reference to a book

    Attributes:
    book -- the reference to the book"""

    def __init__(self) -> None:
        self.book: Book = None


class BetterOptionMenu:
    """Sets up an tkinter options menu

    Parameters:
    master -- the frame the owns the option menu
    options -- an iterable that contains all the options the menu should display

    Attributes:
    strvar
        the string variable associated with the options menu

    box
        the options menu object itself"""

    def __init__(self, master: tk.Frame, options: Iterable[str]) -> None:
        self.strvar = tk.StringVar(value=options[0])
        self.box = tk.OptionMenu(master, self.strvar, *options)
        configure_colours(self.box, colour_scheme=colour_scheme)


class ColumnOption (BetterOptionMenu):
    """an options menu that shows the different fields (columns) in the database

    Parameters:
    master -- the frame the owns the option menu"""

    def __init__(self, master) -> None:
        super().__init__(master,
                         (database_interface.BOOKS_FIELDS[0],)+Book.book_fields+(Book.author_feild, Book.stock_field))


class UserOptions:
    """Gets the sorting and filtering information from the user and applies it to the database

    Parameters:
    root -- the root frame
    database -- the live database link
    update_function -- the function to refresh the UI to match the database"""

    def __init__(self, root, database: database_interface.DataBase, update_func: Callable[[], None]) -> None:
        self.database = database
        self.update_output = update_func
        # set up frame object
        self.frame = tk.Frame(root)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid(sticky="NSEW")
        # setting up options
        self.filter_field = ColumnOption(self.frame)
        self.filter_str = tk.StringVar()
        self.filter = tk.Entry(self.frame, textvariable=self.filter_str)
        configure_colours(self.filter, colour_scheme=colour_scheme)
        self.sorting = ColumnOption(self.frame)
        self.sorting_direction = BetterOptionMenu(self.frame, ("asc", "desc"))
        # gridding into place
        self.filter_field.box.grid(row=0, column=0, sticky="NSEW")
        self.filter.grid(row=0, column=1, sticky="NSEW")
        self.sorting.box.grid(row=0, column=2, sticky="NSEW")
        self.sorting_direction.box.grid(row=0, column=3, sticky="NSEW")
        # bindings
        self.sorting.strvar.trace_add("write", self.update_ordering)
        self.sorting_direction.strvar.trace_add("write", self.update_ordering)
        # so that it can be removed later
        self.database.add_ordering("book_ID")
        self.filter_field.strvar.trace_add("write", self.update_filtering)
        self.filter_str.trace_add("write", self.update_filtering)

    def update_ordering(self, *args) -> None:
        """Sets the order of items displayed to mach that selected by the user

        *args is the event trace information, that is not needed 
        """
        self.database.remove_ordering(0)
        self.database.add_ordering(
            self.sorting.strvar.get(), self.sorting_direction.strvar.get())
        self.update_output()

    def update_filtering(self, *args) -> None:
        """Checks if the entered filter is valid, then sets the filtering of items displayed to mach that selected by the user,

        *args is the event trace information, that is not needed 
        """
        try:
            re.compile(self.filter_str.get())
            configure_colours(self.filter, colour_scheme)
        except re.error:
            configure_colours(self.filter, error_colour_scheme)
            return
        if self.database.generate_filters()[0] != "":
            self.database.remove_filter(0)
        if self.filter_str.get():
            self.database.add_filter(
                self.filter_field.strvar.get(), self.filter_str.get())
        self.update_output()


def add_headings(frame: tk.Frame, row=0) -> None:
    """Adds table headings to a frame

    Parameters:
    frame -- the frame to add the headings to 
    row -- the row that the heading should be placed at (default 0)
    """
    for i, name in enumerate(Book.book_fields+(Book.author_feild, Book.stock_field)):
        border = tk.Frame(frame, background="black", borderwidth=1)
        border.grid_columnconfigure(0, weight=1)
        label = tk.Label(border, text=name[0].upper()+name[1:])
        configure_colours(label, highlight_colour_scheme)
        label.grid(sticky="NSEW")
        border.grid(row=row, column=i, sticky="NSEW")


class BookList:
    """Contains and displays all books

    Parameters:
    root -- the root frame
    database -- the live database link
    active_book -- a bondholder that holds the currently selected book"""

    def __init__(self, root: tk.Frame, database: database_interface.DataBase, active_book: BookHolder) -> None:
        self.frame = tk.Frame(root)
        self.active_book = active_book
        for i in range(6):
            self.frame.columnconfigure(i, weight=1)
        add_headings(self.frame)
        self.frame.grid(row=2, column=0, sticky="NSEW")
        self.displayed_books: List[Book] = []
        self.database = database

    def set_output(self, data: Dict[str, str]) -> None:
        """update the list of displayed books

        Parameters:
        data -- the raw information required to build the list of books, in the desired order"""
        self.data = data
        self.update_output()

    def update_output(self) -> None:
        """updates the displayed books to match the internal data"""
        self.clear_output()
        # length = len(self.data)
        authors = self.database.get_authors()
        for row, book_dict in enumerate(self.data[:50]):
            self.displayed_books.append(
                Book(self.frame, row+1, authors, book_dict, self.database, self.active_book))

    def clear_output(self) -> None:
        """removes all tkinter objects containing current books"""
        for book in self.displayed_books:
            book.destroy()
        self.displayed_books = []


class IncompleteBook:
    """Defines the tkinter objects required for a book
    Does not link to the database as is also used to input new books

    Parameters:
    master -- the frame to place the book in
    row -- the row in the frame to place the book
    author_dictionary -- a dictionary linking authors to their ID"""
    book_fields = database_interface.BOOKS_FIELDS[1:-1]
    author_feild = database_interface.AUTHOR_FIELDS[1]
    stock_field = database_interface.STOCK_FIELDS[1]

    def __init__(self, master: tk.Frame, row: int, author_dictionary: Dict[int, str]) -> None:
        self.master = master
        self.row = row
        self.author_dictionary = author_dictionary
        self.entries = []
        temp = [self.create_element(i) for i in self.book_fields]
        stock = self.create_element(self.stock_field)
        vcmd = (self.master.register(lambda x: x.isdigit() or x == ""))
        stock.configure(validate="all", validatecommand=(vcmd, '%P'))
        self.author = tk.StringVar(master)
        authorbox = tk.OptionMenu(
            master, self.author, *self.author_dictionary.keys())
        authorbox.column_name = self.author_feild
        for x, i in enumerate(temp):
            self.config_element(i, x)
        self.config_element(authorbox, x+1)
        self.config_element(stock, x+2)

    def config_element(self, element: tk.Widget, column: int) -> None:
        """Configures an element

        Parameters:
        element -- the element to be configured
        column -- the desired column in the grid to place the element
        """
        configure_colours(element, colour_scheme)
        element.grid(row=self.row, column=column, sticky="NSEW")
        element.bind("<FocusOut>", lambda x: self.leave_entry(element))
        element.bind("<FocusIn>", lambda x: self.enter_entry(element))
        self.entries.append(element)

    def create_element(self, column_name: str) -> tk.Entry:
        """creates a tkinter entry and associates it with its column

        Parameters:
        column_name -- the name of the column ni the database associated with the entry

        Returns:
        the created entry"""
        entry = tk.Entry(self.master)
        # this is defiantly not a good idea, should use inheritance, but it doesn't change the funtionality.
        entry.column_name = column_name
        return entry

    def leave_entry(self, entry: tk.Entry) -> None:
        """Changes the colour scheme of of the row when the book is deselected

        Parameters:
        entry -- the entry that has been left"""
        for i in self.entries:
            configure_colours(i, colour_scheme)

    def enter_entry(self, entry: tk.Entry) -> None:
        """Changes the colour scheme of of the row when the book is selected and highlights the selected element

        Parameters:
        entry -- the entry that has been entered"""
        for i in self.entries:
            configure_colours(i, highlight_colour_scheme)
        entry.configure(**select_colour_scheme)

    def get_add_dict(self) -> Dict[str, str]:
        """Returns a dictionary of all the data needed to add the book to the database"""
        book_dict = {entry.column_name: entry.get() if isinstance(
            entry, tk.Entry) else self.author.get() for entry in self.entries}
        book_dict[database_interface.AUTHOR_FIELDS[0]
                  ] = self.author_dictionary[book_dict.pop(self.author_feild)]
        return book_dict


class Book (IncompleteBook):
    """Represents a book in the database
    Changes made by the user will be reflected in the database

    Parameters:
    master -- the frame to place the book in
    row -- the row in the frame to place the book
    author_dictionary -- a dictionary linking authors to their ID
    database -- the live database link
    active_book -- a BookHolder that holds the currently selected book"""

    def __init__(self,
                 master: tk.Frame,
                 row: int,
                 author_dictionary: Dict[int, str],
                 book_dict,
                 database: database_interface.DataBase,
                 active_book: BookHolder):
        self.book_dict = book_dict
        super().__init__(master, row, author_dictionary)
        self.database = database
        self.active_book = active_book
        self.ID = book_dict["book_ID"]
        self.author.set(book_dict["author_name"])
        self.author.trace_add("write", self.set_author)

    def create_element(self, column_name: str) -> tk.Entry:
        """extends functionality to creates a tkinter entry amd initialises it with the books data

        Parameters:
        column_name -- the name of the column ni the database associated with the entry

        Returns:
        the created entry"""
        entry = super().create_element(column_name)
        entry.insert(tk.END, str(self.book_dict[column_name]))
        return entry

    def leave_entry(self, entry: tk.Entry) -> None:
        """extends functionality to update the database to match any change to the book

        Parameters:
        entry -- the entry that has been left
        """
        super().leave_entry(entry)
        self.active_book.book = None
        if entry.column_name == self.author_feild:
            return
        elif entry.column_name == self.stock_field:
            self.database.update_stock(self.ID, int(entry.get()))
        else:
            self.database.update_description(
                self.ID, entry.column_name, entry.get())
        self.book_dict[entry.column_name] = entry.get()

    def enter_entry(self, entry: tk.Entry) -> None:
        """extends functionality to set the book to be the active book

        Parameters:
        entry -- the entry that has been entered"""
        super().enter_entry(entry)
        self.active_book.book = self

    def set_author(self, irreleventvalue, irreleventvalue2, irreleventvalue3):
        """sets the author in the database to match the one selected by the user"""
        self.book_dict["author_name"] = self.author.get()
        self.database.update_description(
            self.ID, "author_ID", self.author_dictionary[self.author.get()])

    def destroy(self) -> None:
        """destroys all internal tkinter components"""
        for i in self.entries:
            i.destroy()


class YesNoOptions:
    """displays 2 options in a tkinter toplevel
    the "no" option closes the toplevel
    the "yes" option calls the yes_command and closes the toplevel if it does not return "canceled"

    Parameters:
    popup -- the popup that the options are in
    update_output -- the function to refresh the UI to match the database
    yes_message -- the message associated with the "yes" option
    no_message -- the message associated with the "no" option
    yes_command -- the function to be ran if yes is clicked, returns "canceled" or None
    default_button -- "yes" or "no", the button to default to if the user presses enter (default "no") 
    """

    def __init__(self, popup: tk.Toplevel, update_output: Callable[[], None | str], yes_message: str, no_message: str, yes_command: Callable[[], None], default_button="no") -> None:
        self.popup: tk.Toplevel = popup
        self.yes_command = yes_command
        self.update_output = update_output
        options = tk.Frame(popup, bg=colour_scheme["bg"])
        options.grid(sticky="NSEW", columnspan=6)
        for column, weight in enumerate((5, 1, 1, 1, 5)):
            options.grid_columnconfigure(column, weight=weight)
        no_button = tk.Button(options, text=no_message, command=popup.destroy)
        configure_colours(no_button, colour_scheme)
        no_button.grid(row=0, column=1, sticky="NSEW")
        yes_button = tk.Button(options, text=yes_message,
                               command=self.yes_clicked)
        configure_colours(yes_button, colour_scheme)
        yes_button.grid(row=0, column=3, sticky="NSEW")
        default_button = no_button if default_button == "no" else yes_button
        default_button.focus()
        popup.bind('<Return>', lambda e: default_button.invoke())

    def yes_clicked(self) -> None:
        """calls the yes_command and closes the toplevel if it does not return "canceled"
        """
        result = self.yes_command()
        if result == "canceled":
            self.popup.lift()
        else:
            self.update_output()
            self.popup.destroy()


class Menu:
    """Displays the following utilities options to the user:
        Adding a book
        Deleting a book
        Adding an author
        Deleting an author

    Parameters:
    root -- the root frame
    database -- the live database link
    update_function -- the function to refresh the UI to match the database
    active_book -- a bondholder that holds the currently selected book
    """

    def __init__(self, root: tk.Frame, database: database_interface.DataBase, update_function: Callable[[], None], active_book: BookHolder) -> None:
        self.database = database
        self.active_book = active_book
        self.update_output = update_function
        self.frame = tk.Frame(root, background=colour_scheme["bg"])
        self.frame.grid_rowconfigure(0, weight=1)
        # self.frame.grid_columnconfigure(0,weight=1)
        self.frame.grid(sticky="NSEW")
        for index, (text, command) in enumerate(
                (
                    ("add book", self.ask_added_book),
                    ("delete book", self.confirm_delete_book),
                    ("add author", self.ask_add_author),
                    ("delete author", self.ask_delete_author),
                )):
            button = tk.Button(self.frame, text=text, command=command)
            configure_colours(button, colour_scheme)
            button.grid(row=0, column=index, sticky="NSEW")

    def confirm_delete_book(self) -> None:
        """displays a preview of the currently selected book to ensure the user wants to delete it
        deletes the book if the user confirms"""
        if self.active_book.book == None:
            messagebox.showwarning(
                title="", message="You must select a book before you can delete it")
        else:
            popup = tk.Toplevel(self.frame)
            for i in range(6):
                popup.columnconfigure(i, weight=1)
            are_you_sure = tk.Label(
                popup, text="Are you sure you want to delete this book?", font=("Arial", 14))
            configure_colours(are_you_sure, colour_scheme)
            are_you_sure.grid(sticky="NSEW", columnspan=6)
            add_headings(popup, 1)
            diplayed_book = Book(popup, 2, {1: self.active_book.book.author},
                                 self.active_book.book.book_dict, self.database, BookHolder())
            options = YesNoOptions(popup, self.update_output, "Yes", "No", lambda book=self.active_book.book: self.database.delete_book(
                book.ID))  # contain the book so this popup is always associated with this book

    def ask_added_book(self) -> None:
        """asks the user to enter all the necessary information to add a book"""
        popup = tk.Toplevel(self.frame)
        for i in range(6):
            popup.columnconfigure(i, weight=1)
        lable = tk.Label(popup, text="Add a Book", font=("Arial", 14))
        configure_colours(lable, colour_scheme)
        # need to re-grid for columnnsapn
        lable.grid(sticky="NSEW", columnspan=6)
        add_headings(popup, 1)
        book = IncompleteBook(popup, 2, self.database.get_authors())
        options = YesNoOptions(
            popup, self.update_output, "Add", "Cancel", lambda: self.add_book(book), "yes")

    def add_book(self, book: IncompleteBook) -> str | None:
        """checks if user entered data is valid, and adds the book if it is

        Arguments:
        book -- the tkinter book to check and add

        Returns:
        "canceled" -- the user has not entered valid data and should retry
        None -- the function successfully returned"""
        try:
            book_dict = book.get_add_dict()
        except KeyError:
            messagebox.showinfo("error adding book", "please select an author")
            return "canceled"
        self.database.add_book(book_dict)

    def ask_add_author(self) -> None:
        """asks the user to enter an author and adds it"""
        popup = tk.Toplevel(self.frame)
        popup.columnconfigure(0, weight=1)
        label = tk.Label(popup, text="Add an Author", font=("Arial", 14))
        configure_colours(label, colour_scheme)
        label.grid(sticky="NSEW")
        author = tk.Entry(popup)
        configure_colours(author, colour_scheme)
        author.grid(row=1, column=0, sticky="NSEW")
        options = YesNoOptions(popup, self.update_output, "Add", "Cancel",
                               lambda: self.database.add_author(author.get()), "yes")

    def ask_delete_author(self) -> None:
        """asks the user to select an author to delete and removes it"""
        popup = tk.Toplevel(self.frame)
        popup.columnconfigure(0, weight=1)
        label = tk.Label(
            popup, text="Please Select an Author to delete", font=("Arial", 14))
        configure_colours(label, colour_scheme)
        label.grid(sticky="NSEW")
        author_dict = self.database.get_authors()
        author = BetterOptionMenu(popup, tuple(author_dict.keys()))
        author.box.grid(sticky="NSEW")
        options = YesNoOptions(popup, self.update_output, "Delete", "Cancel",
                               lambda: self.database.delete_author(author_dict[author.strvar.get()]))


if __name__ == "__main__":
    # d = DataBase()
    # book = {"name":"peter pan","ISBN_num": "37872","date":"yesterday","description":"it exists","author_ID":1}
    # for i in range (10000,20000):
    #     d.delete_book(i)
    # d.add_book(book)
    # d.commit()
    ui = UserInterface()
