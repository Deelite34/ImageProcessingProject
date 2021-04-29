import os
import unittest
from time import sleep
import threading
from math import floor
import tkinter as tk
from PIL import ImageTk
from PIL import Image
import matplotlib.pyplot as plt
import c_ops


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

        self.loaded_image_data = []  # Original image [path, editable_tada, tuple(PIL_DATA)] - do not modify this
        self.edited_image_data = []  # Edited image [path, editable_tada, list(PIL_DATA)] - place modified image here
        self.selected_image_data = None
        self.pil_image_data = None
        self.selected_image_data = None

    def donothing(self):
        print("ApoProjectCore class donothing() debug func")


class MenuBarFile(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def load_image(self, parent):
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
            parent.menu_bar.lab_menu_2.entryconfig(0, state=tk.NORMAL)
            parent.menu_bar.lab_menu_2.entryconfig(1, state=tk.NORMAL)
            parent.menu_bar.lab_menu_2.entryconfig(2, state=tk.NORMAL)
            parent.menu_bar.lab_menu_2.entryconfig(3, state=tk.NORMAL)
            parent.menu_bar.lab_menu_2.entryconfig(4, state=tk.NORMAL)
            parent.menu_bar.lab_menu_2.entryconfig(5, state=tk.NORMAL)
            parent.menu_bar.lab_menu_2.entryconfig(6, state=tk.NORMAL)

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

    def save_image(self, parent):
        """
        Basic image saving, needs working on
        """

        # self.edited_image_data.putdata(self.loaded_image_data[1])
        path = tk.filedialog.asksaveasfilename(filetypes=(('Bitmap file', '.bmp'),
                                                       ("Any", '.*'),))  # self.loaded_image_data[0][-3:]
        parent.helper_image_data.save(path + ".bmp", format='BMP')


class MenuBarLab1(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def display_file_content(self, parent):
        try:
            print(parent.loaded_image_data[1][:20])
        except Exception as e:
            print("Załaduj obraz!", e)

    def display_colour_type(self, parent, display=True):
        """
        Print type of image - color, greyscale or binary
        """
        # If 0-th element is tuple(with RGB values) and not number(luminence for pixel)
        if type(parent.loaded_image_data[1][0]).__name__ == "tuple":
            if display:
                print("kolorowy")
            return 'c'  # Colour
        else:
            for value in parent.loaded_image_data[1]:
                binary_values = [0, 255]
                if value not in binary_values:
                    if display:
                        print("Czarnobialy")
                    return "gs"  # GreyScale
            if display:
                print("Binarny")
            return "b"  # Binary

    def create_histogram(self, parent):
        if self.display_colour_type(parent, display=False) == 'gs' or \
                self.display_colour_type(parent, display=False) == 'b':
            self.create_histogram_greyscale(parent)
        else:
            self.create_histogram_color(parent)

    def create_histogram_greyscale(self, parent, img=None):
        """
        Displays histogram for greyscale image.
        img=None parameter allows to prevent certain issue
        """
        img = parent.selected_image_data

        # List with occurrences of each luminance value
        values_count = [0 for i in range(256)]
        for value in img[1]:
            values_count[value] += 1

        x_axis = tuple([i for i in range(256)])
        y_axis = values_count
        plt.title(f"Histogram - {img[0]}")
        plt.bar(x_axis, y_axis)
        plt.show()

    def create_histogram_color(self, parent):
        """
        Splits color image into separate channels and
        displays histogram for each
        """
        img = parent.selected_image_data
        y_axis = [0 for i in range(256)]
        x_axis = [i for i in range(256)]

        def compute_values_count(channel_index):
            for value in img[1]:
                luminence_value = int(value[channel_index])
                y_axis[luminence_value] += 1

        compute_values_count(0)

        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał czerwony - {img[0]}')  # Red channel

        y_axis = [0 for i in range(256)]
        compute_values_count(1)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał zielony - {img[0]}')  # Green channel

        y_axis = [0 for i in range(256)]
        compute_values_count(2)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał niebieski - {img[0]}')  # Blue channel

        plt.show()


class MenuBarLab2(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def display_file_content(self, parent):
        try:
            print(parent.loaded_image_data[1][:20])
        except Exception as e:
            print("Załaduj obraz!", e)

    def histogram_stretch(self, parent):
        """
        Stretches the histogram to max range (to 0-255)
        """
        self.histogram_stretch_calculations(parent, 0, 255)

    def histogram_stretch_calculations(self, parent, l_min, l_max):
        values_count = [0 for i in range(256)]
        for value in parent.loaded_image_data[1]:
            values_count[value] += 1

        for index, number in enumerate(values_count):
            if number:
                first_nonzero_index = index
                break
        for index, number in enumerate(values_count[::-1]):
            if number:
                # print(index, number, len(self.loaded_image_data))
                first_nonzero_index_reverse = 255 - index
                break

        for index in range(len(parent.edited_image_data[1])):
            if parent.edited_image_data[1][index] < l_min:
                parent.edited_image_data[1][index] = l_min
            if parent.edited_image_data[1][index] > l_max:
                parent.edited_image_data[1][index] = l_max
            else:
                parent.edited_image_data[1][index] = \
                    ((parent.edited_image_data[1][index] - first_nonzero_index) * l_max) / \
                    (first_nonzero_index_reverse - first_nonzero_index)
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)

        parent.helper_image_data.putdata(parent.edited_image_data[1])
        self.histogram_stretch_result_window(parent)

    def histogram_stretch_result_window(self, parent):
        stretch_result_window = tk.Toplevel(parent)
        stretch_result_window.title(f"Obraz wynikowy: rozciąganie")
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(stretch_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["Stretched", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        stretch_result_window.mainloop()

    def image_equalize(self, parent):
        cdf = c_ops.calc_cdf(parent.loaded_image_data[1])

        # Lowest value from cdf other than 0
        cdf_min = min(list(filter(lambda x: x != 0, cdf.values())))

        m = parent.loaded_image_data[2].size[0]
        n = parent.loaded_image_data[2].size[1]

        def calculate_eq_v(value):
            return round(((cdf[value] - cdf_min) / ((m * n) - cdf_min)) * 255)

        def make_image_eq_v(original):
            result = []
            for pixel in original:
                result.append(calculate_eq_v(pixel))
            return result

        image_equalized = make_image_eq_v(parent.loaded_image_data[1])
        equalize_result_window = tk.Toplevel(parent)
        equalize_result_window.title(f"Obraz wynikowy: equalizacja")
        picture_label = tk.Label(equalize_result_window)
        picture_label.pack()

        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_equalized)

        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_equalized)

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                              Image.ANTIALIAS)

        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        equalize_result_window.mainloop()

    def image_negate(self, parent):
        """ Negate image and display it"""
        min_v = parent.loaded_image_data[1][0]
        max_v = parent.loaded_image_data[1][0]
        image_negated = list(parent.loaded_image_data[1])

        for pixel in parent.loaded_image_data[1]:
            if pixel > max_v:
                max_v = pixel
            if pixel < min_v:
                min_v = pixel

        for index in range(len(parent.loaded_image_data[1])):
            image_negated[index] = max_v - parent.loaded_image_data[1][index]

        negate_result_window = tk.Toplevel(parent)
        negate_result_window.title(f"Obraz wynikowy: negacja")
        picture_label = tk.Label(negate_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_negated)
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_negated)
        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        negate_result_window.mainloop()

    def image_threshold(self, parent):
        self.menu_stretch_settings_window = tk.Toplevel(parent)
        self.menu_stretch_settings_window.title("Ustawienia progowania")
        self.menu_stretch_settings_window.resizable(False, False)
        self.menu_stretch_settings_window.geometry("300x80")
        self.menu_stretch_settings_window.focus_set()
        label = tk.Label(self.menu_stretch_settings_window, text="Próg", justify=tk.LEFT, anchor='w')

        entry = tk.Entry(self.menu_stretch_settings_window, width=10)
        button = tk.Button(self.menu_stretch_settings_window, text="Wykonaj", width=10,
                           command=lambda: self.image_threshold_calculations(parent, int(entry.get())))

        label.pack()
        entry.pack()
        button.pack()

    def image_threshold_calculations(self, parent, value):
        image_thresholded = list(parent.loaded_image_data[1])
        self.menu_stretch_settings_window.destroy()
        for index in range(len(parent.loaded_image_data[1])):
            if parent.loaded_image_data[1][index] > value:
                image_thresholded[index] = 255
            else:
                image_thresholded[index] = 0

        threshold_result_window = tk.Toplevel()
        threshold_result_window.title(f"Obraz wynikowy: negacja")
        picture_label = tk.Label(threshold_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                        parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_thresholded)
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                           parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_thresholded)
        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                         Image.ANTIALIAS)
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        threshold_result_window.mainloop()

    def image_threshold_double(self, parent):
        # Set threshold level window
        self.menu_stretch_settings_window = tk.Toplevel(parent)
        self.menu_stretch_settings_window.resizable(False, False)
        self.menu_stretch_settings_window.title("Thresholding settings")
        self.menu_stretch_settings_window.focus_set()

        stretch_options_top = tk.Frame(self.menu_stretch_settings_window, width=150, height=150)
        label_1 = tk.Label(stretch_options_top, text="Próg dolny", padx=10, pady=10)
        label_2 = tk.Label(stretch_options_top, text="Próg górny", padx=10, pady=10)
        entry_1 = tk.Entry(stretch_options_top, width=10)
        entry_2 = tk.Entry(stretch_options_top, width=10)

        button_area = tk.Frame(self.menu_stretch_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_threshold_double_calculations(parent, int(entry_1.get()),
                                                                                    int(entry_2.get())))
        button.pack()

        stretch_options_top.grid(column=1, row=0)
        label_1.grid(column=1, row=1, padx=(55, 5))
        label_2.grid(column=2, row=1, padx=(5, 55))
        entry_1.grid(column=1, row=2, padx=(55, 5))
        entry_2.grid(column=2, row=2, padx=(5, 55))
        button_area.grid(column=1, row=1)


    def image_threshold_double_calculations(self, parent, val_floor, val_celling):
        self.menu_stretch_settings_window.destroy()
        image_thresholded = list(parent.loaded_image_data[1])

        for index in range(len(parent.loaded_image_data[1])):
            if parent.loaded_image_data[1][index] > val_celling:
                image_thresholded[index] = 255
            elif parent.loaded_image_data[1][index] <= val_floor:
                image_thresholded[index] = 0

        threshold_result_window = tk.Toplevel()
        threshold_result_window.title(f"Obraz wynikowy: negacja")
        picture_label = tk.Label(threshold_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_thresholded)
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_thresholded)
        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        threshold_result_window.mainloop()

    def image_posterize(self, parent):
        self.stretch_settings_window = tk.Toplevel(parent)
        self.stretch_settings_window.title("Ustawienia posteryzacji")
        self.stretch_settings_window.resizable(False, False)
        self.stretch_settings_window.geometry("300x80")
        self.stretch_settings_window.focus_set()

        label = tk.Label(self.stretch_settings_window, text="Ilość progów")
        entry = tk.Entry(self.stretch_settings_window, width=10)
        button = tk.Button(self.stretch_settings_window, text="Wykonaj", width=10,
                           command=lambda: self.image_posterize_calculations(parent, int(entry.get())))
        label.pack()
        entry.pack()
        button.pack()

    def image_posterize_calculations(self, parent, value):
        image_thresholded = list(parent.loaded_image_data[1])

        self.stretch_settings_window.destroy()
        base_range = floor(255 / value)
        base_value = floor(255 / (value - 1))

        ranges = [index * base_range for index in range(1, value + 1)]
        values = [index * base_value for index in range(0, value)]
        ranges[-1] = values[-1] = 255

        image_posterized = [0] * len(parent.loaded_image_data[1])
        # print(ranges, values)

        for pixel_index in range(len(parent.loaded_image_data[1])):
            for range_index, post_range in enumerate(ranges):
                if parent.loaded_image_data[1][pixel_index] < ranges[range_index]:
                    image_posterized[pixel_index] = values[range_index]
                    break

        # print(parent.loaded_image_data[1][:40], image_posterized[:40])

        posterize_result_window = tk.Toplevel(parent)
        posterize_result_window.title(f"Obraz wynikowy: posteryzacja")
        picture_label = tk.Label(posterize_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_posterized)
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_posterized)
        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                              Image.ANTIALIAS)
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        posterize_result_window.mainloop()

    def histogram_stretch_from_to(self, parent):
        # Uses self, to allow removal of window in histogram stretch result window method
        self.stretch_from_to_settings_window = tk.Toplevel(parent)
        self.stretch_from_to_settings_window.resizable(False, False)
        self.stretch_from_to_settings_window.title("Rozciąganie obrazu")
        self.stretch_from_to_settings_window.focus_set()

        stretch_settings_top = tk.Frame(self.stretch_from_to_settings_window, width=150, height=150)
        label_1 = tk.Label(stretch_settings_top, text="Od - Min", padx=10)
        label_2 = tk.Label(stretch_settings_top, text="Od - Max", padx=10)
        entry_1 = tk.Entry(stretch_settings_top, width=10)
        entry_2 = tk.Entry(stretch_settings_top, width=10)

        label_3 = tk.Label(stretch_settings_top, text="Do - Min", padx=10)
        label_4 = tk.Label(stretch_settings_top, text="Do - Max", padx=10)
        entry_3 = tk.Entry(stretch_settings_top, width=10)
        entry_4 = tk.Entry(stretch_settings_top, width=10)

        button_area = tk.Frame(self.stretch_from_to_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.histogram_stretch_from_to_calculations(parent,
                                                                                       int(entry_1.get()),
                                                                                       int(entry_2.get()),
                                                                                       int(entry_3.get()),
                                                                                       int(entry_4.get())))
        button.pack()
        stretch_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        label_3.grid(column=3, row=0, padx=(15, 5))
        label_4.grid(column=4, row=0, padx=(5, 20))

        entry_1.grid(column=0, row=1, padx=(20, 5))
        entry_2.grid(column=1, row=1, padx=(5, 15))
        entry_3.grid(column=3, row=1, padx=(15, 5))
        entry_4.grid(column=4, row=1, padx=(5, 20))
        button_area.grid(column=0, row=1)

    def histogram_stretch_from_to_calculations(self, parent, from_min, from_max, to_min, to_max):
        values_count = [0 for i in range(256)]
        for value in parent.loaded_image_data[1]:
            values_count[value] += 1

        # Rozciaga histogram do maksymalnego zakresu - obraz czarnobialo = [0,255]
        for index, number in enumerate(values_count):
            if number:
                first_nonzero_index = index
                break
        for index, number in enumerate(values_count[::-1]):
            if number:
                # print(index, number, len(self.loaded_image_data))
                first_nonzero_index_reverse = 255 - index
                break
        #print("Lmin i Lmax:", l_min, l_max)
        #print("min i max:", first_nonzero_index, first_nonzero_index_reverse)
        for index in range(len(parent.edited_image_data[1])):
            if parent.edited_image_data[1][index] < from_min:
                parent.edited_image_data[1][index] = from_min
            if parent.edited_image_data[1][index] > from_max:
                parent.edited_image_data[1][index] = from_max
            else:
                parent.edited_image_data[1][index] = \
                    ((parent.edited_image_data[1][index] - first_nonzero_index) * from_max) / \
                    (first_nonzero_index_reverse - first_nonzero_index)
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)

        parent.helper_image_data.putdata(parent.edited_image_data[1])
        self.histogram_stretch_from_to_result_window(parent)

    def histogram_stretch_from_to_result_window(self, parent):
        self.stretch_from_to_settings_window.destroy()
        stretch_result_window = tk.Toplevel()
        stretch_result_window.title(f"Obraz wynikowy: rozciąganie zakresu do zakresu")
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(stretch_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                         Image.ANTIALIAS)
        parent.selected_image_data = ["Stretched", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        stretch_result_window.mainloop()


class MenuBarHelp(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def about(self, parent):
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

        self.menu_bar_help = MenuBarHelp()
        self.menu_bar_file = MenuBarFile()
        self.menu_bar_lab1 = MenuBarLab1()
        self.menu_bar_lab2 = MenuBarLab2()

    def menu_bar_fill(self, parent):
        self.add_cascade(label="Plik", menu=self.file_menu)
        self.file_menu.add_command(label="Nowy", command=parent.donothing, state=tk.DISABLED)
        self.file_menu.add_command(label="Otwórz", command=lambda: self.menu_bar_file.load_image(parent))
        self.file_menu.add_command(label="Zapisz", command=lambda: self.menu_bar_file.save_image(parent))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Nic nie rób", command=parent.donothing)

        self.add_cascade(label="Labolatorium 1", menu=self.lab_menu_1)
        self.lab_menu_1.add_command(label="Co jest w pliku?",
                                    command=lambda: self.menu_bar_lab1.display_file_content(parent),
                                    state=tk.DISABLED)
        self.lab_menu_1.add_command(label="Typ obrazu", command=lambda: self.menu_bar_lab1.display_colour_type(parent),
                                    state=tk.DISABLED)
        self.lab_menu_1.add_command(label="Histogram", command=lambda: self.menu_bar_lab1.create_histogram(parent),
                                    state=tk.DISABLED)

        self.add_cascade(label="Labolatorium 2", menu=self.lab_menu_2)
        self.lab_menu_2.add_command(label="Rozciąganie histogramu",
                                    command=lambda: self.menu_bar_lab2.histogram_stretch(parent),
                                    state=tk.DISABLED)
        self.lab_menu_2.add_command(label="Wyrównywanie histogramu przez equalizację",
                                    command=lambda: self.menu_bar_lab2.image_equalize(parent),
                                    state=tk.DISABLED)
        self.lab_menu_2.add_command(label="Negacja", command=lambda: self.menu_bar_lab2.image_negate(parent),
                                    state=tk.DISABLED)
        self.lab_menu_2.add_command(label="Progowanie", command=lambda: self.menu_bar_lab2.image_threshold(parent),
                                    state=tk.DISABLED)
        self.lab_menu_2.add_command(label="Progowanie z zach. poz. szarości",
                                    command=lambda: self.menu_bar_lab2.image_threshold_double(parent),
                                    state=tk.DISABLED)
        self.lab_menu_2.add_command(label="Posteryzacja do red. poz. szarości",
                                    command=lambda: self.menu_bar_lab2.image_posterize(parent),
                                    state=tk.DISABLED)
        self.lab_menu_2.add_command(label="Rozciąganie histogramu od zakresu do zakresu",
                                    command=lambda: self.menu_bar_lab2.histogram_stretch_from_to(parent),
                                    state=tk.DISABLED)

        self.add_cascade(label="Labolatorium 3", menu=self.lab_menu_3)

        self.add_cascade(label="Pomoc", menu=self.helpmenu)
        self.helpmenu.add_command(label="O aplikacji", command=lambda: self.menu_bar_help.about(parent))
        self.helpmenu.add_command(label="Jakas komenda", command=parent.donothing)


if __name__ == "__main__":
    app = ApoProjectCore()
    app.mainloop()
