# TKINTER OOP
# Use Tkinter for python 2, tkinter for python 3
import os
import unittest
from time import sleep
import threading
from math import floor
import tkinter as tk
from PIL import ImageTk
from PIL import Image
import matplotlib.pyplot as plt

class ApoProjectCore(tk.Tk):
    """
    Outermost class of the project
    Controls main window, initialises adding commands to menubar elements
    Calls another classess as needed
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Projekt")
        self.geometry("500x100")

        self.menu_bar = MenuBarAdd(self)
        self.config(menu=self.menu_bar)  # Adds menu bar to the main window

        self.resize_width = 500
        self.resize_height = 500

        self.loaded_image_data = []  # Original image [path, editable_tada, tuple(PIL_DATA)] - do not modify
        self.edited_image_data = []  # Edited image [path, editable_tada, list(PIL_DATA)] - place modified image here
        self.selected_image_data = []  #



    def menu_init_file_open(self):
        MenuBarFile().menu_file_load_image(self)

    def menu_init_help_about(self):
        MenuBarHelp().menu_help_about(self)

    def donothing(self):
        print("ApoProjectCore class donothing() debug func")


class MenuBarFile(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)
        #self.menu_help_about(parent)

    def menu_file_load_image(self, parent):
        """
        Opens selected image in separate window
        """
        # Opens menu allowing to select path to picture
        img_path = tk.filedialog.askopenfilename(initialdir=os.getcwd())
        # Assigns picture to variable
        if img_path:
            # Enables buttons in top menu
            parent.menu_bar.lab_menu_1.entryconfig(0, state=tk.NORMAL)
            parent.menu_bar.lab_menu_1.entryconfig(1, state=tk.NORMAL)
            parent.menu_bar.lab_menu_1.entryconfig(2, state=tk.NORMAL)
            window = tk.Toplevel(parent)
            window.title(f"Obraz pierwotny - {os.path.basename(img_path)}")
            image = Image.open(img_path)
            parent.loaded_image_data = [os.path.basename(img_path), tuple(image.getdata()), image]
            parent.edited_image_data = [parent.loaded_image_data[0], list(parent.loaded_image_data[1])]
            parent.selected_image_data = [os.path.basename(img_path), list(image.getdata()), image]

            image.resize((parent.resize_width, parent.resize_height), Image.ANTIALIAS)
            selected_picture = ImageTk.PhotoImage(image)
            picture_label = tk.Label(window)
            picture_label.configure(image=selected_picture)
            picture_label.pack()
            window.mainloop()
        else:
            print("Image was not chosen")

class MenuBarHelp(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def menu_help_about(self, parent):
        """
        Displays 'O aplikacji' - about menu
        """
        about_window = tk.Toplevel(parent)
        about_window.title("O aplikacji")
        about_window.resizable(False, False)
        about_window.focus_set()

        bg_col = "#2C2F33"
        fg_col = "#BBBBBB"
        mainframe = tk.Frame(about_window, padx="70", pady="15", bg=bg_col)  #
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        tk.Label(mainframe, text="Autor: Deelite34, Grupa: xxxxxxx ", bg=bg_col, fg=fg_col
                 ).grid(sticky=tk.N, column=1, row=1)
        tk.Label(mainframe, text="Projekt w ramach przedmiotu", bg=bg_col, fg=fg_col
                 ).grid(sticky=tk.N, column=1, row=2)
        tk.Label(mainframe, text="Program wykonany w języku Python wersja 3.8", bg=bg_col, fg=fg_col
                 ).grid(column=1, row=3)
        tk.Label(mainframe, text="", bg=bg_col, fg=fg_col
                 ).grid(column=1, row=4)
        tk.Button(mainframe, text="Zamknij", bg=bg_col, fg=fg_col, activebackground=bg_col,
                  activeforeground=fg_col, command=about_window.destroy
                  ).grid(column=1, row=5)


class MenuBarAdd(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.file_menu = tk.Menu(self, tearoff=0)
        self.lab_menu_1 = tk.Menu(self, tearoff=0)
        self.lab_menu_2 = tk.Menu(self, tearoff=0)
        self.lab_menu_3 = tk.Menu(self, tearoff=0)
        self.helpmenu = tk.Menu(self, tearoff=0)
        self.menu_bar_fill(parent)

    def menu_bar_fill(self, parent):
        self.add_cascade(label="Plik", menu=self.file_menu)
        self.file_menu.add_command(label="Nowy", command=parent.donothing, state=tk.DISABLED)
        self.file_menu.add_command(label="Otwórz", command=parent.menu_init_file_open)
        self.file_menu.add_command(label="Zapisz", command=parent.donothing)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Nic nie rób", command=parent.donothing)

        self.add_cascade(label="Labolatorium 1", menu=self.lab_menu_1)
        self.lab_menu_1.add_command(label="Co jest w pliku?", command=parent.donothing, state=tk.DISABLED)
        self.lab_menu_1.add_command(label="Typ obrazu", command=parent.donothing, state=tk.DISABLED)
        self.lab_menu_1.add_command(label="Histogram", command=parent.donothing, state=tk.DISABLED)

        self.add_cascade(label="Labolatorium 2", menu=self.lab_menu_2)
        self.lab_menu_2.add_command(label="Rozciąganie histogramu", command=parent.donothing)
        self.lab_menu_2.add_command(label="Wyrównywanie histogramu przez equalizację",
                               command=parent.donothing)
        self.lab_menu_2.add_command(label="Negacja", command=parent.donothing)
        self.lab_menu_2.add_command(label="Progowanie", command=parent.donothing)
        self.lab_menu_2.add_command(label="Progowanie z zach. poz. szarości", command=parent.donothing)
        self.lab_menu_2.add_command(label="Posteryzacja do red. poz. szarości", command=parent.donothing)
        self.lab_menu_2.add_command(label="Rozciąganie histogramu od zakresu do zakresu",
                               command=parent.donothing)
        self.lab_menu_2.add_command(label="Wypisz aktywne okno tkinter", command=parent.donothing)

        self.add_cascade(label="Labolatorium 3", menu=self.lab_menu_3)

        self.add_cascade(label="Pomoc", menu=self.helpmenu)
        self.helpmenu.add_command(label="O aplikacji", command=parent.menu_init_help_about)
        self.helpmenu.add_command(label="Jakas komenda", command=parent.donothing)


if __name__ == "__main__":
    app = ApoProjectCore()
    app.mainloop()
