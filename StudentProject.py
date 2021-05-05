import os
import unittest
from time import sleep
import threading
from math import floor
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from PIL import Image
import matplotlib.pyplot as plt
import c_ops
import cv2
import numpy


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
        self.cv2_image = None
        self.selected_image_data = None
        self.pil_image_data = None
        self.selected_image_data = None
        self.all_open_image_data = {}

        self.open_windows = []  # You can append tk.Toplevel(parentname), then call open_windows[0].geometry("100x100")

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
            last_1 = parent.menu_bar.lab_menu_1.index("end")
            last_2 = parent.menu_bar.lab_menu_2.index("end")
            last_3 = parent.menu_bar.lab_menu_3.index("end")
            last_4 = parent.menu_bar.lab_menu_4.index("end")
            for i in range(last_1 + 1):
                parent.menu_bar.lab_menu_1.entryconfig(i, state=tk.NORMAL)
            for i in range(last_2 + 1):
                parent.menu_bar.lab_menu_2.entryconfig(i, state=tk.NORMAL)
            for i in range(last_3 + 1):
                parent.menu_bar.lab_menu_3.entryconfig(i, state=tk.NORMAL)
            #for i in range(last_4 + 1):
            #    parent.menu_bar.lab_menu_4.entryconfig(i, state=tk.NORMAL)

            window = tk.Toplevel(parent)
            title = f"Obraz pierwotny - {os.path.basename(img_path)}"
            helper_index = 0
            while title in parent.all_open_image_data.keys():
                helper_index += 1
                title = f"Obraz pierwotny ({str(helper_index)}) - {os.path.basename(img_path)}"
            window.title(title)

            def on_closing():
                del parent.all_open_image_data[title]
                window.destroy()

            window.protocol("WM_DELETE_WINDOW", on_closing)

            image = Image.open(img_path)
            parent.loaded_image_data = [os.path.basename(img_path), tuple(image.getdata()), image]
            parent.edited_image_data = [parent.loaded_image_data[0], list(parent.loaded_image_data[1])]
            parent.selected_image_data = [os.path.basename(img_path), list(image.getdata()), image]
            #parent.all_open_image_data[title] = list(parent.loaded_image_data[1])
            parent.all_open_image_data[title] = Image.open(img_path)

            parent.cv2_image = cv2.imread(img_path, 0)

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
                                                          ("Any", '.*'),))
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

    def visible_images(self, parent):
        print(parent.all_open_image_data.keys())


class MenuBarLab2(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

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
        img_title = "Obraz wynikowy - rozciąganie"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = "Obraz wynikowy - rozciąganie " + f"({str(helper_index)})"
        stretch_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            stretch_result_window.destroy()

        stretch_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
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
        img_title = "Obraz wynikowy - equalizacja"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = "Obraz wynikowy - equalizacja " + f"({str(helper_index)})"
        equalize_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            equalize_result_window.destroy()

        equalize_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        picture_label = tk.Label(equalize_result_window)
        picture_label.pack()

        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_equalized)
        parent.all_open_image_data[img_title] = parent.pil_image_data

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
        img_title = "Obraz wynikowy - negacja"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - negacja({str(helper_index)})"
        negate_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            negate_result_window.destroy()

        negate_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        picture_label = tk.Label(negate_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_negated)
        parent.all_open_image_data[img_title] = parent.pil_image_data
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
        img_title = "Obraz wynikowy - progowanie"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - progowanie({str(helper_index)})"
        threshold_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            threshold_result_window.destroy()

        threshold_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        picture_label = tk.Label(threshold_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_thresholded)
        parent.all_open_image_data[img_title] = parent.pil_image_data
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

        threshold_double_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - progowanie z zakresem"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - progowanie z zakresem({str(helper_index)})"
        threshold_double_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            threshold_double_result_window.destroy()

        threshold_double_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        picture_label = tk.Label(threshold_double_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_thresholded)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_thresholded)
        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        threshold_double_result_window.mainloop()

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
        self.stretch_settings_window.destroy()
        base_range = floor(255 / value)
        base_value = floor(255 / (value - 1))

        ranges = [index * base_range for index in range(1, value + 1)]
        values = [index * base_value for index in range(0, value)]
        ranges[-1] = values[-1] = 255

        image_posterized = [0] * len(parent.loaded_image_data[1])

        for pixel_index in range(len(parent.loaded_image_data[1])):
            for range_index, post_range in enumerate(ranges):
                if parent.loaded_image_data[1][pixel_index] < ranges[range_index]:
                    image_posterized[pixel_index] = values[range_index]
                    break

        # print(parent.loaded_image_data[1][:40], image_posterized[:40])

        posterize_result_window = tk.Toplevel(parent)
        img_title = "Obraz wynikowy - posteryzacja"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - posteryzacja({str(helper_index)})"
        posterize_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            posterize_result_window.destroy()

        posterize_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        picture_label = tk.Label(posterize_result_window)
        picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_posterized)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)
        parent.helper_image_data.putdata(image_posterized)
        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        posterize_result_window.mainloop()

    def histogram_stretch_from_to(self, parent):
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

        for index in range(len(parent.edited_image_data[1])):
            if parent.edited_image_data[1][index] < from_min:
                parent.edited_image_data[1][index] = from_min
            if parent.edited_image_data[1][index] > from_max:
                parent.edited_image_data[1][index] = from_max
            else:
                parent.edited_image_data[1][index] = \
                    (((parent.edited_image_data[1][index] - from_min) * (to_max - to_min)) /
                     (from_max - from_min)) + to_min
        parent.helper_image_data = Image.new(parent.loaded_image_data[2].mode,
                                             parent.loaded_image_data[2].size)

        parent.helper_image_data.putdata(parent.edited_image_data[1])
        self.histogram_stretch_from_to_result_window(parent)

    def histogram_stretch_from_to_result_window(self, parent):
        self.stretch_from_to_settings_window.destroy()
        stretch_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - rozciąganie od zakresu do zakresu"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - rozciąganie od zakresu do zakresu({str(helper_index)})"
        stretch_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            stretch_result_window.destroy()

        stretch_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
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


class MenuBarLab3(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)
        self.items = {"Izolacja": cv2.BORDER_ISOLATED,
                      "Odbicie": cv2.BORDER_REFLECT,
                      "Replikacja": cv2.BORDER_REPLICATE}

    def image_linear_smoothing(self, parent):
        self.image_linear_smoothing_window = tk.Toplevel(parent)
        self.image_linear_smoothing_window.resizable(False, False)
        self.image_linear_smoothing_window.title("Ustawienia")
        self.image_linear_smoothing_window.focus_set()

        math_not_settings_top = tk.Frame(self.image_linear_smoothing_window, width=150, height=150)
        label_1 = tk.Label(math_not_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(math_not_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        button_area = tk.Frame(self.image_linear_smoothing_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_linear_smoothing_controler(
                                                    parent,
                                                    self.items[combobox_1.get()]))
        button.pack()
        math_not_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def image_linear_smoothing_controler(self, parent, border):
        parent.edited_image_data[1] = self.image_linear_smoothing_calculate(parent, border)
        self.image_linear_smoothing_result_window(parent)

    def image_linear_smoothing_calculate(self, parent, border):
        result = cv2.blur(parent.loaded_image_data[1], (5, 5), 0, borderType=border)
        result = [_[0] for _ in result]
        return result

    def image_linear_smoothing_result_window(self, parent):
        self.image_linear_smoothing_window.destroy()
        smoothing_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - wygładzanie liniowe"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - wygładzanie liniowe({str(helper_index)})"
        smoothing_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            smoothing_result_window.destroy()

        smoothing_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(smoothing_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["Linear smoothing", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        smoothing_result_window.mainloop()

    def image_gauss_linear_smoothing(self, parent):
        self.image_linear_smoothing_window = tk.Toplevel(parent)
        self.image_linear_smoothing_window.resizable(False, False)
        self.image_linear_smoothing_window.title("Ustawienia")
        self.image_linear_smoothing_window.focus_set()

        gauss_linear_smoothing_settings_top = tk.Frame(self.image_linear_smoothing_window, width=150, height=150)
        label_1 = tk.Label(gauss_linear_smoothing_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(gauss_linear_smoothing_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        button_area = tk.Frame(self.image_linear_smoothing_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_gauss_linear_smoothing_controler(
                                                  parent,
                                                  self.items[combobox_1.get()]))
        button.pack()
        gauss_linear_smoothing_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def image_gauss_linear_smoothing_controler(self, parent, border):
        parent.edited_image_data[1] = self.image_gauss_linear_smoothing_calculate(parent, border)
        self.image_gauss_linear_smoothing_result_window(parent)

    def image_gauss_linear_smoothing_calculate(self, parent, border):
        result = cv2.GaussianBlur(parent.loaded_image_data[1], (3, 3), 0, borderType=border)
        result = [_[0] for _ in result]
        return result

    def image_gauss_linear_smoothing_result_window(self, parent):
        gauss_smoothing_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - wygładzanie liniowe gaussa"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - wygładzanie liniowe({str(helper_index)})"
        gauss_smoothing_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            gauss_smoothing_result_window.destroy()

        gauss_smoothing_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(gauss_smoothing_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["Linear smoothing", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        gauss_smoothing_result_window.mainloop()

    def image_laplacian(self, parent):
        self.image_laplacian_window = tk.Toplevel(parent)
        self.image_laplacian_window.resizable(False, False)
        self.image_laplacian_window.title("Ustawienia")
        self.image_laplacian_window.focus_set()

        image_laplacian_settings_top = tk.Frame(self.image_laplacian_window, width=150, height=150)
        label_1 = tk.Label(image_laplacian_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(image_laplacian_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        button_area = tk.Frame(self.image_laplacian_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_laplacian_controler(
                                                   parent,
                                                   self.items[combobox_1.get()]))
        button.pack()
        image_laplacian_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def image_laplacian_controler(self, parent, border):
        parent.edited_image_data[1] = self.image_laplacian_calculate(parent, border)
        self.image_laplacian_result_window(parent)

    def image_laplacian_calculate(self, parent, border):
        ddepth = cv2.CV_64F
        ksize = 3
        result = cv2.Laplacian(parent.loaded_image_data[1], ddepth, ksize, borderType=border)
        result = [_[0] for _ in result]
        return result

    def image_laplacian_result_window(self, parent):
        laplacian_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - detekcja krawędzi met. laplacian"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - detekcja krawędzi met. laplacian({str(helper_index)})"
        laplacian_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            laplacian_result_window.destroy()

        laplacian_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(laplacian_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["Laplacian", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        laplacian_result_window.mainloop()

    def image_sobel(self, parent):
        self.image_sobel_window = tk.Toplevel(parent)
        self.image_sobel_window.resizable(False, False)
        self.image_sobel_window.title("Ustawienia")
        self.image_sobel_window.focus_set()

        image_sobel_settings_top = tk.Frame(self.image_sobel_window, width=150, height=150)
        label_1 = tk.Label(image_sobel_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(image_sobel_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        button_area = tk.Frame(self.image_sobel_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_sobel_controler(
                               parent,
                               self.items[combobox_1.get()]))
        button.pack()
        image_sobel_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def image_sobel_controler(self, parent, border):
        parent.edited_image_data[1] = self.image_sobel_calculate(parent, border)
        self.image_sobel_result_window(parent)

    def image_sobel_calculate(self, parent, border):
        sobelx = cv2.Sobel(parent.cv2_image, cv2.CV_64F, 1, 0, ksize=5, borderType=border)
        sobely = cv2.Sobel(parent.cv2_image, cv2.CV_64F, 0, 1, ksize=5, borderType=border)

        im_pil = Image.fromarray(sobelx).getdata()
        return im_pil

    def image_sobel_result_window(self, parent):
        sobel_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - detekcja krawędzi met. sobel"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - detekcja krawędzi met. sobel({str(helper_index)})"
        sobel_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            sobel_result_window.destroy()

        sobel_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(sobel_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["sobel", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        sobel_result_window.mainloop()

    def image_canny(self, parent):
        parent.edited_image_data[1] = self.image_canny_calculate(parent)
        self.image_canny_result_window(parent)

    def image_canny_calculate(self, parent):
        threshold1 = 100
        threshold2 = 200
        img_canny = cv2.Canny(parent.cv2_image, threshold1, threshold2)
        im_pil = Image.fromarray(img_canny).getdata()
        return im_pil

    def image_canny_result_window(self, parent):
        canny_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - detekcja krawędzi met. canny"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - detekcja krawędzi met. canny({str(helper_index)})"
        canny_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            canny_result_window.destroy()

        canny_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(canny_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["canny", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        canny_result_window.mainloop()

    def image_sharpening(self, parent):
        self.image_sharpening_window = tk.Toplevel(parent)
        self.image_sharpening_window.resizable(False, False)
        self.image_sharpening_window.title("Ustawienia")
        self.image_sharpening_window.focus_set()

        image_sharpening_settings_top = tk.Frame(self.image_sharpening_window, width=150, height=150)
        label_1 = tk.Label(image_sharpening_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(image_sharpening_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        mask_values = {"Maska 1 - [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]": 0,
                      "Maska 2 - [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]": 1,
                      "Maska 3 - [[1, -2, 1], [-2, 5, -2], [1, -2, 1]]": 2}

        label_2 = tk.Label(image_sharpening_settings_top, text="Wybór maski", padx=10)
        combobox_2 = ttk.Combobox(image_sharpening_settings_top, state='readonly', width=45)
        combobox_2["values"] = list(mask_values.keys())
        combobox_2.current(0)

        button_area = tk.Frame(self.image_sharpening_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_sharpening_controler(
                               parent,
                               self.items[combobox_1.get()],
                               mask_values[combobox_2.get()]))
        button.pack()
        image_sharpening_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        label_2.grid(column=0, row=2, padx=(25, 5))
        combobox_2.grid(column=0, row=3, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def image_sharpening_controler(self, parent, border, selected):
        parent.edited_image_data[1] = self.image_sharpening_calculate(parent, border, selected)
        self.image_sharpening_window.destroy()
        self.image_sharpening_result_window(parent)

    def image_sharpening_calculate(self, parent, border, selected):
        mask_sharp = [numpy.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]),
                      numpy.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]),
                      numpy.array([[1, -2, 1], [-2, 5, -2], [1, -2, 1]])]

        img_sharp = cv2.filter2D(parent.cv2_image, cv2.CV_64F, mask_sharp[selected], borderType=border)
        im_pil = Image.fromarray(img_sharp).getdata()
        return im_pil

    def image_sharpening_result_window(self, parent):
        sharpening_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - wyostrzanie liniowe"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - detekcja krawędzi met. canny({str(helper_index)})"
        sharpening_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            sharpening_result_window.destroy()

        sharpening_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(sharpening_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["sharpening", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        sharpening_result_window.mainloop()

    def image_edge_detection(self, parent):
        self.image_edge_detection_window = tk.Toplevel(parent)
        self.image_edge_detection_window.resizable(False, False)
        self.image_edge_detection_window.title("Ustawienia")
        self.image_edge_detection_window.focus_set()
        mask_values = {"Maska NW - [[+1, +1, 0], [+1, 0, -1], [0, -1, -1]]": 0,
                       "Maska N - [[+1, +1, +1], [0, 0, 0], [-1, -1, -1]]": 1,
                       "Maska NE - [[0, +1, +1], [-1, 0, +1], [-1, -1, 0]]": 2,
                       "Maska E - [[-1, 0, +1], [-1, 0, +1], [-1, 0, +1]]": 3,
                       "Maska SE - [[-1, -1, 0], [-1, 0, +1], [0, +1, +1]]": 4,
                       "Maska S - [[-1, -1, -1], [0, 0, 0], [+1, +1, +1]]": 5,
                       "Maska SW - [[0, -1, -1], [+1, 0, -1], [+1, +1, 0]]": 6,
                       "Maska W - [[+1, 0, -1], [+1, 0, -1], [+1, 0, -1]]": 7}
        image_edge_detection_settings_top = tk.Frame(self.image_edge_detection_window, width=150, height=150)
        label_1 = tk.Label(image_edge_detection_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(image_edge_detection_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        label_2 = tk.Label(image_edge_detection_settings_top, text="Wybór maski", padx=10)
        combobox_2 = ttk.Combobox(image_edge_detection_settings_top, state='readonly', width=45)
        combobox_2["values"] = list(mask_values.keys())
        combobox_2.current(0)

        button_area = tk.Frame(self.image_edge_detection_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.image_edge_detection_controler(
                               parent,
                               self.items[combobox_1.get()],
                               mask_values[combobox_2.get()]))
        button.pack()
        image_edge_detection_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        label_2.grid(column=0, row=2, padx=(25, 5))
        combobox_2.grid(column=0, row=3, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def image_edge_detection_controler(self, parent, border, mask):
        parent.edited_image_data[1] = self.image_edge_detection_calculate(parent, border, mask)
        self.image_edge_detection_result_window(parent)

    def image_edge_detection_calculate(self, parent, border, mask):
        mask_values = [numpy.array([[+1, +1, 0], [+1, 0, -1], [0, -1, -1]]),
                       numpy.array([[+1, +1, +1], [0, 0, 0], [-1, -1, -1]]),
                       numpy.array([[0, +1, +1], [-1, 0, +1], [-1, -1, 0]]),
                       numpy.array([[-1, 0, +1], [-1, 0, +1], [-1, 0, +1]]),
                       numpy.array([[-1, -1, 0], [-1, 0, +1], [0, +1, +1]]),
                       numpy.array([[-1, -1, -1], [0, 0, 0], [+1, +1, +1]]),
                       numpy.array([[0, -1, -1], [+1, 0, -1], [+1, +1, 0]]),
                       numpy.array([[+1, 0, -1], [+1, 0, -1], [+1, 0, -1]])]

        img_prewitt = cv2.filter2D(parent.cv2_image, cv2.CV_64F, mask_values[mask], borderType=border)
        im_pil = Image.fromarray(img_prewitt).getdata()
        return im_pil

    def image_edge_detection_result_window(self, parent):
        self.image_edge_detection_window.destroy()
        edge_detection_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - kierunkowe wykrywanie krawędzi"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - kierunkowe wykrywanie krawędzi({str(helper_index)})"
        edge_detection_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            edge_detection_result_window.destroy()

        edge_detection_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(edge_detection_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["edge_detection", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        edge_detection_result_window.mainloop()

    def linear_neighbour_op(self, parent):
        self.linear_neighbour_op_window = tk.Toplevel(parent)
        self.linear_neighbour_op_window.resizable(False, False)
        self.linear_neighbour_op_window.title("Ustawienia")
        self.linear_neighbour_op_window.focus_set()


        linear_neighbour_op_settings_top = tk.Frame(self.linear_neighbour_op_window, width=300, height=150, )
        label_1 = tk.Label(linear_neighbour_op_settings_top, text="Ustawienia pikseli brzegowych", padx=10, pady=10)
        label_1.pack()
        combobox_1 = ttk.Combobox(linear_neighbour_op_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.items.keys())
        combobox_1.current(0)

        text_area = tk.Frame(self.linear_neighbour_op_window, width=100, pady=10, height=50)
        label_2 = tk.Label(text_area, text="Wypełnij macierz maski 3x3", padx=10)
        label_2.pack()

        linear_neighbour_op_settings_grid = tk.Frame(self.linear_neighbour_op_window, width=300, height=300)
        entry_1 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_2 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_3 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_4 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_5 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_6 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_7 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_8 = tk.Entry(linear_neighbour_op_settings_grid, width=5)
        entry_9 = tk.Entry(linear_neighbour_op_settings_grid, width=5)

        button_area = tk.Frame(self.linear_neighbour_op_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.linear_neighbour_op_calculations(parent, int(entry_1.get()),
                                                                                         int(entry_2.get()),
                                                                                         int(entry_3.get()),
                                                                                         int(entry_4.get()),
                                                                                         int(entry_5.get()),
                                                                                         int(entry_6.get()),
                                                                                         int(entry_7.get()),
                                                                                         int(entry_8.get()),
                                                                                         int(entry_9.get())))
        button.pack()
        linear_neighbour_op_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=1)
        combobox_1.grid(column=0, row=2)
        text_area.grid(column=0, row=1)
        label_2.grid(column=0, row=3)
        linear_neighbour_op_settings_grid.grid(column=0, row=2)
        entry_1.grid(column=0, row=1, padx=(20, 5))
        entry_2.grid(column=1, row=1, padx=(5, 5))
        entry_3.grid(column=2, row=1, padx=(5, 15))
        entry_4.grid(column=0, row=2, padx=(20, 5))
        entry_5.grid(column=1, row=2, padx=(5, 5))
        entry_6.grid(column=2, row=2, padx=(5, 20))
        entry_7.grid(column=0, row=3, padx=(20, 5))
        entry_8.grid(column=1, row=3, padx=(5, 5))
        entry_9.grid(column=2, row=3, padx=(5, 20))
        button_area.grid(column=0, row=4)

    def linear_neighbour_op_calculations(self, parent, xy_11, xy_21, xy_31,
                                                       xy_12, xy_22, xy_32,
                                                       xy_13, xy_23, xy_33):
        requirements = sum([xy_11, xy_21, xy_31, xy_12, xy_22, xy_32, xy_13, xy_23, xy_33]) != 0 and \
                       all([xy_11, xy_21, xy_31, xy_12, xy_22, xy_32, xy_13, xy_23, xy_33])
        if requirements is False:
            return  # requirements not fulfilled, do not continue

        self.linear_neighbour_op_window.destroy()
        inp_values = [xy_11, xy_21, xy_31, xy_12, xy_22, xy_32, xy_13, xy_23, xy_33]
        kernel = numpy.zeros((3, 3))
        index = 0
        for i in range(3):
            for j in range(3):
                kernel[i, j] = inp_values[index]
                index += 1

        kernel = numpy.int64(kernel) / numpy.sum(kernel)
        numpy.sum(kernel)
        img_filtered = cv2.filter2D(parent.cv2_image, cv2.CV_64F, kernel, borderType=cv2.BORDER_REPLICATE)

        parent.edited_image_data[1] = Image.fromarray(img_filtered).getdata()

        linear_neighbour_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - uniwersalna operacja liniowa sąsiedztwa"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - uniwersalna operacja liniowa sąsiedztwa({str(helper_index)})"
        linear_neighbour_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            linear_neighbour_result_window.destroy()

        linear_neighbour_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(linear_neighbour_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["Neightbour_op", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        linear_neighbour_result_window.mainloop()

    def median_filter(self, parent):
        parent.edited_image_data[1] = self.median_filter_calculate(parent)
        self.median_filter_result_window(parent)

    def median_filter_calculate(self, parent):
        median_blured_img = cv2.medianBlur(parent.cv2_image, 11)
        im_pil = Image.fromarray(median_blured_img).getdata()
        return im_pil

    def median_filter_result_window(self, parent):
        median_filter_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - filtracja medianowa"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - filtracja medianowa({str(helper_index)})"
        median_filter_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            median_filter_result_window.destroy()

        median_filter_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_data[2].mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(median_filter_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["median_filter", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        median_filter_result_window.mainloop()

    def math_add(self, parent):
        self.math_add_settings_window = tk.Toplevel(parent)
        self.math_add_settings_window.resizable(False, False)
        self.math_add_settings_window.title("Dodawanie - wybierz obrazy")
        self.math_add_settings_window.focus_set()

        math_add_settings_top = tk.Frame(self.math_add_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_add_settings_top, text="Obraz 1", padx=10)
        label_2 = tk.Label(math_add_settings_top, text="Obraz 2", padx=10)

        combobox_1 = ttk.Combobox(math_add_settings_top, state='readonly', width=45)
        combobox_1["values"] = items
        combobox_2 = ttk.Combobox(math_add_settings_top, state='readonly', width=45)
        combobox_2["values"] = items

        button_area = tk.Frame(self.math_add_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_add_controler(
                                                        parent,
                                                        combobox_1.get(),
                                                        combobox_2.get()))
        button.pack()
        math_add_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        combobox_2.grid(column=1, row=1, padx=(5, 15))
        button_area.grid(column=0, row=1)

    def math_add_controler(self, parent, img_one, img_two):
        parent.edited_image_data[1] = self.math_add_calculations(parent, img_one, img_two)
        self.math_add_result_window(parent, img_one)

    def math_add_calculations(self, parent, img_one, img_two):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        print(first_cv2.shape[1])
        print(first_cv2.shape[0])
        print(type(first_cv2))

        second_arg = numpy.array(parent.all_open_image_data[img_two])
        second_cv2 = cv2.resize(second_arg, (first_cv2.shape[1], first_cv2.shape[0]))
        print(type(second_cv2))
        add_result = cv2.add(first_cv2, second_cv2)
        print(type(add_result))


        result = Image.fromarray(add_result).getdata()
        return result

    def math_add_result_window(self, parent, img_one):
        self.math_add_settings_window.destroy()
        math_add_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - dodawanie"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - dodawanie({str(helper_index)})"
        math_add_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_add_result_window.destroy()

        math_add_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_add_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["Added", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_add_result_window.mainloop()

    def math_subtract(self, parent):
        self.math_subtract_settings_window = tk.Toplevel(parent)
        self.math_subtract_settings_window.resizable(False, False)
        self.math_subtract_settings_window.title("Dodawanie - wybierz obrazy")
        self.math_subtract_settings_window.focus_set()

        math_subtract_settings_top = tk.Frame(self.math_subtract_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_subtract_settings_top, text="Obraz 1", padx=10)
        label_2 = tk.Label(math_subtract_settings_top, text="Obraz 2", padx=10)

        combobox_1 = ttk.Combobox(math_subtract_settings_top, state='readonly', width=45)
        combobox_1["values"] = items
        combobox_2 = ttk.Combobox(math_subtract_settings_top, state='readonly', width=45)
        combobox_2["values"] = items

        button_area = tk.Frame(self.math_subtract_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_subtract_controler(
                                                        parent,
                                                        combobox_1.get(),
                                                        combobox_2.get()))
        button.pack()
        math_subtract_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        combobox_2.grid(column=1, row=1, padx=(5, 15))
        button_area.grid(column=0, row=1)

    def math_subtract_controler(self, parent, img_one, img_two):
        parent.edited_image_data[1] = self.math_subtract_calculations(parent, img_one, img_two)
        self.math_subtract_result_window(parent, img_one)

    def math_subtract_calculations(self, parent, img_one, img_two):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        second_cv2 = cv2.resize(numpy.array(parent.all_open_image_data[img_two]),
                                (first_cv2.shape[1], first_cv2.shape[0]))
        subtract_result = cv2.subtract(first_cv2, second_cv2)
        result = Image.fromarray(subtract_result).getdata()
        return result

    def math_subtract_result_window(self, parent, img_one):
        self.math_subtract_settings_window.destroy()
        math_subtract_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - odejmowanie"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - odejmowanie({str(helper_index)})"
        math_subtract_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_subtract_result_window.destroy()

        math_subtract_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_subtract_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["subtracted", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_subtract_result_window.mainloop()

    def math_blend(self, parent):
        self.math_blend_settings_window = tk.Toplevel(parent)
        self.math_blend_settings_window.resizable(False, False)
        self.math_blend_settings_window.title("Dodawanie - wybierz obrazy")
        self.math_blend_settings_window.focus_set()

        math_blend_settings_top = tk.Frame(self.math_blend_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_blend_settings_top, text="Obraz 1", padx=10)
        label_2 = tk.Label(math_blend_settings_top, text="Obraz 2", padx=10)
        label_3 = tk.Label(math_blend_settings_top, text="Waga 1", padx=10)
        label_4 = tk.Label(math_blend_settings_top, text="Waga 2", padx=10)
        label_5 = tk.Label(math_blend_settings_top, text="Gamma", padx=10)

        combobox_1 = ttk.Combobox(math_blend_settings_top, state='readonly', width=45)
        combobox_1["values"] = items
        combobox_2 = ttk.Combobox(math_blend_settings_top, state='readonly', width=45)
        combobox_2["values"] = items
        entry_1 = tk.Entry(math_blend_settings_top, width=10)
        entry_2 = tk.Entry(math_blend_settings_top, width=10)
        entry_3 = tk.Entry(math_blend_settings_top, width=10)

        button_area = tk.Frame(self.math_blend_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_blend_controler(
                                                        parent,
                                                        combobox_1.get(),
                                                        combobox_2.get(),
                                                        entry_1.get(),
                                                        entry_2.get(),
                                                        entry_3.get()))
        button.pack()
        math_blend_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        label_3.grid(column=0, row=2, padx=(25, 5))
        label_4.grid(column=1, row=2, padx=(5, 15))
        label_5.grid(column=0, row=5, padx=(25, 5))
        entry_1.grid(column=0, row=4, padx=(20, 5))
        entry_2.grid(column=1, row=4, padx=(5, 15))
        entry_3.grid(column=0, row=6, padx=(20, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        combobox_2.grid(column=1, row=1, padx=(5, 15))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def math_blend_controler(self, parent, img_one, img_two, weight_one, weight_two, gamma_val):
        parent.edited_image_data[1] = self.math_blend_calculations(parent, img_one, img_two,
                                                                   weight_one, weight_two, gamma_val)
        self.math_blend_result_window(parent, img_one)

    def math_blend_calculations(self, parent, img_one, img_two, weight_one, weight_two, gamma_val):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        second_cv2 = cv2.resize(numpy.array(parent.all_open_image_data[img_two]),
                                (first_cv2.shape[1], first_cv2.shape[0]))

        blend_result = cv2.addWeighted(first_cv2, float(weight_one), second_cv2, float(weight_two), float(gamma_val))
        result = Image.fromarray(blend_result).getdata()
        return result

    def math_blend_result_window(self, parent, img_one):
        self.math_blend_settings_window.destroy()
        math_blend_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - dodawanie"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - dodawanie({str(helper_index)})"
        math_blend_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_blend_result_window.destroy()

        math_blend_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_blend_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["blended", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_blend_result_window.mainloop()

    def math_and(self, parent):
        self.math_and_settings_window = tk.Toplevel(parent)
        self.math_and_settings_window.resizable(False, False)
        self.math_and_settings_window.title("Operacja AND - wybierz obrazy")
        self.math_and_settings_window.focus_set()

        math_and_settings_top = tk.Frame(self.math_and_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_and_settings_top, text="Obraz 1", padx=10)
        label_2 = tk.Label(math_and_settings_top, text="Obraz 2", padx=10)

        combobox_1 = ttk.Combobox(math_and_settings_top, state='readonly', width=45)
        combobox_1["values"] = items
        combobox_2 = ttk.Combobox(math_and_settings_top, state='readonly', width=45)
        combobox_2["values"] = items

        button_area = tk.Frame(self.math_and_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_and_controler(
                                                        parent,
                                                        combobox_1.get(),
                                                        combobox_2.get()))
        button.pack()
        math_and_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        combobox_2.grid(column=1, row=1, padx=(5, 15))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def math_and_controler(self, parent, img_one, img_two):
        parent.edited_image_data[1] = self.math_and_calculations(parent, img_one, img_two)
        self.math_and_result_window(parent, img_one)

    def math_and_calculations(self, parent, img_one, img_two):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        second_cv2 = cv2.resize(numpy.array(parent.all_open_image_data[img_two]),
                                (first_cv2.shape[1], first_cv2.shape[0]))

        and_result = cv2.bitwise_and(first_cv2, second_cv2)
        result = Image.fromarray(and_result).getdata()
        return result

    def math_and_result_window(self, parent, img_one):
        self.math_and_settings_window.destroy()
        math_and_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - AND"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - AND({str(helper_index)})"
        math_and_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_and_result_window.destroy()

        math_and_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_and_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["and", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_and_result_window.mainloop()

    def math_or(self, parent):
        self.math_or_settings_window = tk.Toplevel(parent)
        self.math_or_settings_window.resizable(False, False)
        self.math_or_settings_window.title("Operacja or - wybierz obrazy")
        self.math_or_settings_window.focus_set()

        math_or_settings_top = tk.Frame(self.math_or_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_or_settings_top, text="Obraz 1", padx=10)
        label_2 = tk.Label(math_or_settings_top, text="Obraz 2", padx=10)

        combobox_1 = ttk.Combobox(math_or_settings_top, state='readonly', width=45)
        combobox_1["values"] = items
        combobox_2 = ttk.Combobox(math_or_settings_top, state='readonly', width=45)
        combobox_2["values"] = items

        button_area = tk.Frame(self.math_or_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_or_controler(
                                                        parent,
                                                        combobox_1.get(),
                                                        combobox_2.get()))
        button.pack()
        math_or_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        combobox_2.grid(column=1, row=1, padx=(5, 15))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def math_or_controler(self, parent, img_one, img_two):
        parent.edited_image_data[1] = self.math_or_calculations(parent, img_one, img_two)
        self.math_or_result_window(parent, img_one)

    def math_or_calculations(self, parent, img_one, img_two):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        second_cv2 = cv2.resize(numpy.array(parent.all_open_image_data[img_two]),
                                (first_cv2.shape[1], first_cv2.shape[0]))

        or_result = cv2.bitwise_or(first_cv2, second_cv2)
        result = Image.fromarray(or_result).getdata()
        return result

    def math_or_result_window(self, parent, img_one):
        self.math_or_settings_window.destroy()
        math_or_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - OR"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - OR({str(helper_index)})"
        math_or_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_or_result_window.destroy()

        math_or_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_or_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["or", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_or_result_window.mainloop()

    def math_not(self, parent):
        self.math_not_settings_window = tk.Toplevel(parent)
        self.math_not_settings_window.resizable(False, False)
        self.math_not_settings_window.title("Operacja not - wybierz obrazy")
        self.math_not_settings_window.focus_set()

        math_not_settings_top = tk.Frame(self.math_not_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_not_settings_top, text="Obraz 1", padx=10)

        combobox_1 = ttk.Combobox(math_not_settings_top, state='readonly', width=45)
        combobox_1["values"] = items

        button_area = tk.Frame(self.math_not_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_not_controler(
                                                        parent,
                                                        combobox_1.get()))
        button.pack()
        math_not_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def math_not_controler(self, parent, img_one):
        parent.edited_image_data[1] = self.math_not_calculations(parent, img_one)
        self.math_not_result_window(parent, img_one)

    def math_not_calculations(self, parent, img_one):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        not_result = cv2.bitwise_not(first_cv2)
        result = Image.fromarray(not_result).getdata()
        return result

    def math_not_result_window(self, parent, img_one):
        self.math_not_settings_window.destroy()
        math_not_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - not"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - not({str(helper_index)})"
        math_not_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_not_result_window.destroy()

        math_not_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_not_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["not", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_not_result_window.mainloop()

    def math_xor(self, parent):
        self.math_xor_settings_window = tk.Toplevel(parent)
        self.math_xor_settings_window.resizable(False, False)
        self.math_xor_settings_window.title("Operacja xor - wybierz obrazy")
        self.math_xor_settings_window.focus_set()

        math_xor_settings_top = tk.Frame(self.math_xor_settings_window, width=150, height=150)
        items = [_ for _ in parent.all_open_image_data.keys()]

        label_1 = tk.Label(math_xor_settings_top, text="Obraz 1", padx=10)
        label_2 = tk.Label(math_xor_settings_top, text="Obraz 2", padx=10)

        combobox_1 = ttk.Combobox(math_xor_settings_top, state='readonly', width=45)
        combobox_1["values"] = items
        combobox_2 = ttk.Combobox(math_xor_settings_top, state='readonly', width=45)
        combobox_2["values"] = items

        button_area = tk.Frame(self.math_xor_settings_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.math_xor_controler(
                                                        parent,
                                                        combobox_1.get(),
                                                        combobox_2.get()))
        button.pack()
        math_xor_settings_top.grid(column=0, row=0)
        label_1.grid(column=0, row=0, padx=(25, 5))
        label_2.grid(column=1, row=0, padx=(5, 15))
        combobox_1.grid(column=0, row=1, padx=(20, 5))
        combobox_2.grid(column=1, row=1, padx=(5, 15))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def math_xor_controler(self, parent, img_one, img_two):
        parent.edited_image_data[1] = self.math_xor_calculations(parent, img_one, img_two)
        self.math_xor_result_window(parent, img_one)

    def math_xor_calculations(self, parent, img_one, img_two):
        first_cv2 = numpy.array(parent.all_open_image_data[img_one])
        second_cv2 = cv2.resize(numpy.array(parent.all_open_image_data[img_two]),
                                (first_cv2.shape[1], first_cv2.shape[0]))

        xor_result = cv2.bitwise_xor(first_cv2, second_cv2)
        result = Image.fromarray(xor_result).getdata()
        return result

    def math_xor_result_window(self, parent, img_one):
        self.math_xor_settings_window.destroy()
        math_xor_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - xor"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - xor({str(helper_index)})"
        math_xor_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            math_xor_result_window.destroy()

        math_xor_result_window.protocol("WM_DELETE_WINDOW", on_closing)

        parent.pil_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                          parent.all_open_image_data[img_one].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_xor_result_window)
        picture_label.pack()

        parent.pil_image_data = parent.pil_image_data.resize((parent.resize_width, parent.resize_height),
                                                             Image.ANTIALIAS)
        parent.selected_image_data = ["xor", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_xor_result_window.mainloop()


class MenuBarLab4(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)


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
        self.lab_menu_3_math_cascade = tk.Menu(self.lab_menu_3, tearoff=0)
        self.lab_menu_4 = tk.Menu(self, tearoff=0)
        self.helpmenu = tk.Menu(self, tearoff=0)
        self.menu_bar_fill(parent)

        self.menu_bar_help = MenuBarHelp()
        self.menu_bar_file = MenuBarFile()
        self.menu_bar_lab1 = MenuBarLab1()
        self.menu_bar_lab2 = MenuBarLab2()
        self.menu_bar_lab3 = MenuBarLab3()
        self.menu_bar_lab4 = MenuBarLab4()

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
        self.lab_menu_1.add_command(label="Wypisz widoczne obrazy",
                                    command=lambda: self.menu_bar_lab1.visible_images(parent),
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
        self.lab_menu_3.add_command(label="Wygładzanie liniowe", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_linear_smoothing(parent))
        self.lab_menu_3.add_command(label="Wygładzanie liniowe gaussa", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_gauss_linear_smoothing(parent))
        self.lab_menu_3.add_command(label="Detekcja krawędzi laplacian", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_laplacian(parent))
        self.lab_menu_3.add_command(label="Detekcja krawędzi sobel", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_sobel(parent))
        self.lab_menu_3.add_command(label="Detekcja krawędzi canny", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_canny(parent))
        self.lab_menu_3.add_command(label="Wyostrzanie liniowe", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_sharpening(parent))
        self.lab_menu_3.add_command(label="Kierunkowa detekcja krawędzi", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.image_edge_detection(parent))
        self.lab_menu_3.add_command(label="Operacja liniowa sąsiedztwa", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.linear_neighbour_op(parent))
        self.lab_menu_3.add_command(label="Filtracja medianowa", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab3.median_filter(parent))
        self.lab_menu_3.add_cascade(label="Operacja matematyczne", menu=self.lab_menu_3_math_cascade, state=tk.DISABLED)
        self.lab_menu_3_math_cascade.add_command(label="Dodawanie",
                                                 command=lambda: self.menu_bar_lab3.math_add(parent))
        self.lab_menu_3_math_cascade.add_command(label="Odejmowanie",
                                                 command=lambda: self.menu_bar_lab3.math_subtract(parent))
        self.lab_menu_3_math_cascade.add_command(label="Mieszanie",
                                                 command=lambda: self.menu_bar_lab3.math_blend(parent))
        self.lab_menu_3_math_cascade.add_command(label="AND",
                                                 command=lambda: self.menu_bar_lab3.math_and(parent))
        self.lab_menu_3_math_cascade.add_command(label="OR",
                                                 command=lambda: self.menu_bar_lab3.math_or(parent))
        self.lab_menu_3_math_cascade.add_command(label="NOT",
                                                 command=lambda: self.menu_bar_lab3.math_not(parent))
        self.lab_menu_3_math_cascade.add_command(label="XOR",
                                                 command=lambda: self.menu_bar_lab3.math_xor(parent))

        self.add_cascade(label="Labolatorium 4", menu=self.lab_menu_4)

        self.add_cascade(label="Pomoc", menu=self.helpmenu)
        self.helpmenu.add_command(label="O aplikacji", command=lambda: self.menu_bar_help.about(parent))
        self.helpmenu.add_command(label="Jakas komenda", command=parent.donothing)


if __name__ == "__main__":
    app = ApoProjectCore()
    app.mainloop()
