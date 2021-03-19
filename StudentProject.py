import os
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk
from PIL import Image
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import unittest



class ApoProject:
    def __init__(self):
        self.resize_height = 500
        self.resize_width = 500
        self.image_path = None
        self.root = Tk()
        self.menubar = Menu(self.root)  # Creates empty area that can contain menus
        self.root.title("APO Projekt")
        self.root.geometry("300x300")
        self.bg_default = "#2C2F33"
        self.fg_default = "#BBBBBB"
        self.fg_button_clicked = ""
        #self.open_images_list = []
        #self.loaded_images = []

    def donothing(self):
        print("do nothing function")

    def open_img_as_tuple(self, path=None):
        """ Returns output list where index number:
           [0] is file name,
           [1] contains colour values of image
        """
        if not path:
            path = filedialog.askopenfilename(initialdir=os.getcwd())
        if path:
            img = Image.open(path)#os.path.basename(path)
            print(tuple(img.getdata())[:10])
            print(os.path.basename(path))
            return [os.path.basename(path), tuple(img.getdata())]
        print("Image not chosen")

    def create_histogram_greyscale(self, img=None):
        if img is None:
            img = self.open_img_as_tuple()

        # List with occurrences of each luminance value
        values_count = [0 for i in range(256)]
        for value in img[1]:
            values_count[value] += 1

        x_axis = tuple([i for i in range(256)]) #
        y_axis = values_count
        plt.title(f"Histogram - {img[0]}")
        plt.bar(x_axis, y_axis)
        plt.show()

    def create_histogram_color(self):
        """
        Splits color image into separate channels and
        displays histogram for each
        """
        img = self.open_img_as_tuple()
        y_axis = [0 for i in range(256)]

        def compute_values_count(channel_index):
            for value in img[1]:
                y_axis[value[channel_index]] += 1

        x_axis = [i for i in range(256)]
        compute_values_count(0)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał czerwony - {img[0]}') # Red channel

        compute_values_count(1)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał zielony - {img[0]}') # Green channel

        compute_values_count(2)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał niebieski - {img[0]}') # Blue channel

        plt.show()

    def print_file_content(self):
        """
        Prints file content to console
        """
        arr = self.open_img_as_tuple()[1]
        print(arr)

    def print_image_type(self):
        """ Print type of image - color, greyscale or binary"""
        arr = self.open_img_as_tuple()
        if type(arr[1][0]).__name__ == "tuple":
            print("Obraz kolorowy")
        else:
            print(f"Obraz jest typu: {self.check_greyscale_or_binary(arr)}")

    def check_greyscale_or_binary(self, img):
        """ Description:
            Use only for greyscale images.
            Returns False if image is binary,
            if it is in greyscale, this will return True
            Parameters:
                'img' - tuple filled with numbers
            """
        for value in img:
            test = value
            binary_values = [0, 255]
            if value not in binary_values:
                return "czarno-biały"
        return "binarny"

    def menu_create(self):
        """
        Creates menu on top side of the window
        """
        file_menu = Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Nowy", command=self.donothing)
        file_menu.add_command(label="Otwórz", command=self.menu_file_load_image)
        file_menu.add_command(label="Zapisz", command=self.donothing)
        file_menu.add_separator()
        file_menu.add_command(label="Nic nie rób", command=self.donothing)
        self.menubar.add_cascade(label="Plik", menu=file_menu)
        lab_menu = Menu(self.menubar, tearoff=0)
        lab_menu.add_command(label="Nic nie rób", command=self.donothing)
        lab_menu_1 = Menu(self.menubar, tearoff=0)
        lab_menu_1.add_command(label="Co jest w pliku?", command=self.print_file_content)
        lab_menu_1.add_command(label="Typ obrazu", command=self.print_image_type)
        lab_menu_1.add_command(label="Histogram - czarnobiały", command=self.create_histogram_greyscale)
        lab_menu_1.add_command(label="Histogram - kolorowy", command=self.create_histogram_color)
        self.menubar.add_cascade(label="Labolatorium 1", menu=lab_menu_1)
        self.menubar.add_cascade(label="Labolatorium 2", menu=lab_menu)
        self.menubar.add_cascade(label="Labolatorium 3", menu=lab_menu)
        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="O aplikacji", command=self.menu_help_about)
        self.menubar.add_cascade(label="Pomoc", menu=helpmenu)

    def launch_app(self):
        self.menu_create()
        self.root.config(menu=self.menubar, background=self.bg_default)
        self.root.geometry("500x100")
        self.root.mainloop()

    def menu_help_about(self):
        window = Toplevel()
        window.title("O aplikacji")
        mainframe = Frame(window, padx="70", pady="15", bg=self.bg_default)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        Label(mainframe, text="Autor: Deelite34, Grupa: xxxxxxx ", bg=self.bg_default, fg=self.fg_default
              ).grid(sticky=N, column=1, row=1)
        Label(mainframe, text="Projekt w ramach przedmiotu", bg=self.bg_default, fg=self.fg_default
              ).grid(sticky=N, column=1, row=2)
        Label(mainframe, text="Program wykonany w języku Python wersja 3.8", bg=self.bg_default, fg=self.fg_default
              ).grid(column=1, row=3)
        Label(mainframe, text="", bg=self.bg_default, fg=self.fg_default
              ).grid(column=1, row=4)
        Button(mainframe, text="Zamknij", bg=self.bg_default, fg=self.fg_default, activebackground=self.bg_default,
               activeforeground=self.fg_default, command=window.destroy
               ).grid(column=1, row=5)

    def menu_file_load_image(self):
        """
        Opens selected image in separate window
        """
        # Opens menu allowing to select path to picture
        img_path = filedialog.askopenfilename(initialdir=os.getcwd())
        # Assigns picture to variable
        if img_path:
            root = Toplevel()
            root.title(f"Obraz pierwotny - {os.path.basename(img_path)}")
            picture_label = Label(root)
            picture_label.pack()
            image = Image.open(img_path)
            image = image.resize((self.resize_width, self.resize_height), Image.ANTIALIAS)
            selected_picture = ImageTk.PhotoImage(image)
            picture_label.configure(image=selected_picture)
            self.root.mainloop()
        else:
            print("Image was not chosen")

class TestApoprojectClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_pic_greyscale_dir = f'{os.getcwd()}\\tests\\lena_greyscale.bmp'
        cls.test_pic_greyscale_open = Image.open(cls.test_pic_greyscale_dir)
        cls.test_pic_greyscale_data = tuple(cls.test_pic_greyscale_open.getdata())  # Image data as tuple
        cls.test_pic_colour_dir = f'{os.getcwd()}\\tests\\lena_colour.bmp'
        print(cls.test_pic_colour_dir)
        print(cls.test_pic_greyscale_dir)
        cls.test_pic_colour_open = Image.open(cls.test_pic_colour_dir)
        cls.test_pic_colour_data = tuple(cls.test_pic_colour_open.getdata())  # Image data as tuple
        cls.main = ApoProject()


    def test_open_image_as_tuple(self):
        self.assertEqual(self.test_pic_greyscale_data,
                        self.main.open_img_as_tuple(path=self.test_pic_greyscale_dir)[1])
        self.assertEqual(self.test_pic_colour_data,
                         self.main.open_img_as_tuple(path=self.test_pic_colour_dir)[1])


    def test_histogram_greyscale(self):
        #Todo
        pass

    def test_histogram_color(self):
        #Todo
        pass

if __name__ == "__main__":
    #test = TestApoprojectClass()
    #unittest.main()
    start = ApoProject()
    start.launch_app()
