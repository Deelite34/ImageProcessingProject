from math import floor
from time import sleep
import os
from webbrowser import open_new

import cv2
import numpy
from PIL import Image
from PIL import ImageTk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from scipy.signal import convolve2d as conv2



try:
    from StudentProject import ApoProjectCore
except ImportError as er:
    while True:
        print(er)
        input("Run program trough StudenrProject.py!")


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
            # Enables disabled buttons in top menu
            last_1 = parent.menu_bar.lab_menu_1.index("end")  # index of last elements of specifib menus
            last_2 = parent.menu_bar.lab_menu_2.index("end")
            last_3 = parent.menu_bar.lab_menu_3.index("end")
            last_4 = parent.menu_bar.lab_menu_4.index("end")
            last_5 = parent.menu_bar.lab_menu_5.index("end")
            last_final = parent.menu_bar.lab_menu_final.index("end")
            for i in range(last_1 + 1):  # enable options in specific menus
                parent.menu_bar.lab_menu_1.entryconfig(i, state=tk.NORMAL)
            for i in range(last_2 + 1):
                parent.menu_bar.lab_menu_2.entryconfig(i, state=tk.NORMAL)
            for i in range(last_3 + 1):
                parent.menu_bar.lab_menu_3.entryconfig(i, state=tk.NORMAL)
            for i in range(last_4 + 1):
                parent.menu_bar.lab_menu_4.entryconfig(i, state=tk.NORMAL)
            for i in range(last_5 + 1):
                parent.menu_bar.lab_menu_5.entryconfig(i, state=tk.NORMAL)
            for i in range(last_final + 1):
                parent.menu_bar.lab_menu_final.entryconfig(i, state=tk.NORMAL)

            window = tk.Toplevel(parent)  # create window
            title = f"Obraz pierwotny - {os.path.basename(img_path)}"
            # Ensures window name is unique
            helper_index = 0
            while title in parent.all_open_image_data.keys():
                helper_index += 1
                title = f"Obraz pierwotny ({str(helper_index)}) - {os.path.basename(img_path)}"
            window.title(title)

            def on_closing():
                del parent.all_open_image_data[title]  # remove image from list of open images
                window.destroy()

            # when window is closed use specified function
            window.protocol("WM_DELETE_WINDOW", on_closing)

            # load image either as colour, or greyscale image
            parent.cv2_image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if len(parent.cv2_image.shape) != 3:
                print("Zaladowano czarnobialy")
                parent.cv2_image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            image = Image.open(img_path)
            image.convert("L")
            # img with 3 channels has tuple with values for each channel instead of integer for pixel
            # this ensures greyscale images with 3 channels are made into 1 channel, to allow operations on them
            if isinstance(list(Image.fromarray(parent.cv2_image).getdata())[0], tuple):
                helper = list(Image.fromarray(parent.cv2_image).getdata())
                content = [helper[i][0] for i in range(len(helper))]
                parent.loaded_image_data = [os.path.basename(img_path), content, image]
            else:
                parent.loaded_image_data = [os.path.basename(img_path),
                                            list(Image.fromarray(parent.cv2_image).getdata()),
                                            image]
            parent.edited_image_data = [parent.loaded_image_data[0], parent.loaded_image_data[1]]
            parent.histogram_image_data = [os.path.basename(img_path), list(image.getdata()), image]
            parent.all_open_image_data[title] = Image.open(img_path)

            # Detect if we have colour image with 3 channels, or greyscale image with 3 channels
            if len(parent.cv2_image.shape) == 3:  # Image has 3 channels. Either colour, or .png file
                ch1, ch2, ch3 = cv2.split(parent.cv2_image)  # Image with 3 channels still can be greyscale
                if (not numpy.any(cv2.subtract(ch1, ch2))) and (not numpy.any(cv2.subtract(ch2, ch3))):
                    # Difference of channels in greyscale image results in fully black img
                    parent.cv2_image = cv2.cvtColor(parent.cv2_image, cv2.COLOR_BGR2GRAY)
            parent.loaded_image_type = parent.menu_bar.menu_bar_lab1.display_colour_type(parent)

            selected_picture = ImageTk.PhotoImage(image)
            picture_label = tk.Label(window)
            picture_label.configure(image=selected_picture)
            picture_label.pack()
            window.mainloop()
        else:
            print("Nie wybrano obrazu")

    def save_image(self, parent):
        """
        Image saving
        """

        img_type = tk.StringVar()
        path = tk.filedialog.asksaveasfilename(filetypes=(('BMP', '.bmp'),
                                                          ('PNG', '.png'),
                                                          ('JPEG', '.jpeg')),
                                               typevariable=img_type)
        if path:
            try:
                file_type = img_type.get()
                # prevents situation when overriding existing files, resulting in double extension like .bmp.bmp
                if not path.lower().endswith(('.bmp', '.png', '.jpeg')):
                    parent.save_helper_image_data.save(path + "." + file_type.lower(), format=file_type)
                else:
                    parent.save_helper_image_data.save(path[:-4] + "." + file_type.lower(), format=file_type)
            except AttributeError:  # parent.save_helper_image_data is empty
                print("Najpierw edytuj obraz!")


class MenuBarLab1(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def display_file_content(self, parent):
        """
        Displays some file content in console
        :param parent:
        :return:
        """
        try:
            content = parent.loaded_image_data[1][:20]
        except Exception as e:
            print("Załaduj obraz!", e)

    def display_colour_type(self, parent):
        """
        Checks colour typeo f image
        :param parent:
        :return: string for color type: c, gs, gs3ch, b; colour, greyscale, greyscale 3 channels, binary
        """
        channel_amount = 0
        try:
            test1, test2, test3 = cv2.split(parent.cv2_image)  # split channels content into 3 variables
            channel_amount = 3
        except ValueError:
            channel_amount = 1

        if channel_amount == 3:
            ch1, ch2, ch3 = cv2.split(parent.cv2_image)  # Split image into 3 images for each channel
            # difference between 2 channels in greyscale 3 channel image results in fully black image
            if (not numpy.any(cv2.subtract(ch1, ch2))) and (not numpy.any(cv2.subtract(ch2, ch3))):
                parent.loaded_image_mode = "L"
                return 'gs3ch'
            parent.loaded_image_mode = "RGB"
            return "c"
        elif channel_amount == 1:
            for value in parent.loaded_image_data[1]:
                binary_values = [0, 255]
                parent.loaded_image_mode = "L"
                if isinstance(value, tuple):
                    return 'gs3ch'
                if value not in binary_values:
                    return "gs"  # GreyScale
            return "b"  # Binary

    def create_histogram(self, parent):
        if parent.loaded_image_type == 'gs' or \
                parent.loaded_image_type == 'b' or \
                parent.loaded_image_type == 'gs3ch':
            self.create_histogram_greyscale(parent)
        else:
            self.create_histogram_color(parent)

    def create_histogram_greyscale(self, parent, img=None):
        """
        Displays histogram for greyscale image.
        img=None parameter allows to prevent certain issue
        """
        if parent.loaded_image_type == 'gs3ch':
            # gets values of only first channel of greyscale 3 channel type image
            img = [parent.loaded_image_data[1][i][0] for i in range(len(parent.loaded_image_data[1]))]
        else:
            img = parent.loaded_image_data[1]  # list containing image luminence avlues

        # List with occurrences of each luminance value
        values_count = [0 for i in range(256)]
        for value in img:
            values_count[value] += 1

        x_axis = list([i for i in range(256)])
        y_axis = values_count
        plt.title(f"Histogram - {parent.loaded_image_data[0]}")
        plt.bar(x_axis, y_axis)
        plt.show()

    def create_histogram_color(self, parent):
        """
        Splits color image into separate channels and
        displays histogram for each
        """
        if parent.loaded_image_type == "gs" or \
                parent.loaded_image_type == 'b' or \
                parent.loaded_image_type == 'gs3ch':
            return self.create_histogram_greyscale(parent)
        img = parent.histogram_image_data
        y_axis = [0 for i in range(256)]
        x_axis = [i for i in range(256)]
        red_channel = [i[0] for i in img[1]]
        green_channel = [i[1] for i in img[1]]
        blue_channel = [i[2] for i in img[1]]

        def compute_values_count(channel_name):
            for value in channel_name:
                luminence_value = int(value)
                y_axis[luminence_value] += 1

        compute_values_count(red_channel)

        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał czerwony - {img[0]}')  # Red channel

        y_axis = [0 for i in range(256)]
        compute_values_count(green_channel)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał zielony - {img[0]}')  # Green channel

        y_axis = [0 for i in range(256)]
        compute_values_count(blue_channel)
        plt.figure()
        plt.bar(x_axis, y_axis)
        plt.title(f'Histogram - kanał niebieski - {img[0]}')  # Blue channel

        plt.show()

    def visible_images(self, parent):
        """
        Displays in console which images are open and detected in program
        :param parent:
        """
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
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)

        parent.edited_image_data = list(parent.edited_image_data)
        parent.save_helper_image_data.putdata(tuple(parent.edited_image_data[1]))
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

        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(stretch_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Stretched", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        stretch_result_window.mainloop()

    def image_equalize(self, parent):
        def calc_cdf(image_list):
            cdf = {}
            image_list_sorted = sorted(image_list)
            for number in image_list:
                if number in cdf.keys():
                    continue
                cdf[number] = count_smaller_nums(number, image_list_sorted)
            return cdf

        def count_smaller_nums(number, inp_list):
            count = 0
            for i in inp_list:
                if i <= number:
                    count += 1
                else:
                    return count
            return count

        cdf = calc_cdf(parent.loaded_image_data[1])

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

        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_equalized)
        parent.all_open_image_data[img_title] = parent.pil_image_data

        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(image_equalized)

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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_negated)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(image_negated)

        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        negate_result_window.mainloop()

    def image_threshold(self, parent):
        self.menu_stretch_settings_window = tk.Toplevel(parent)
        self.menu_stretch_settings_window.title("Ustawienia progowania")
        self.menu_stretch_settings_window.resizable(False, False)
        self.menu_stretch_settings_window.geometry("300x80")
        self.menu_stretch_settings_window.focus_set()

        label = tk.Label(self.menu_stretch_settings_window, text="Próg (od 1 do 255)", justify=tk.LEFT, anchor='w')

        entry = tk.Entry(self.menu_stretch_settings_window, width=10)
        entry.insert(0, "1")
        button = tk.Button(self.menu_stretch_settings_window, text="Wykonaj", width=10,
                           command=lambda: self.image_threshold_calculations(parent, entry.get()))

        label.pack()
        entry.pack()
        button.pack()

    def image_threshold_calculations(self, parent, value):
        try:
            int(value)
        except ValueError:
            print("Wpisana wartosc musi byc liczba")
            return
        if not (0 < int(value) < 255):
            print("Wartosc poza zakresem 0-255")
            return
        value = int(value)
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_thresholded)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(image_thresholded)

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
                           command=lambda: self.image_threshold_double_calculations(parent, entry_1.get(),
                                                                                    entry_2.get()))
        button.pack()

        stretch_options_top.grid(column=1, row=0)
        label_1.grid(column=1, row=1, padx=(55, 5))
        label_2.grid(column=2, row=1, padx=(5, 55))
        entry_1.grid(column=1, row=2, padx=(55, 5))
        entry_2.grid(column=2, row=2, padx=(5, 55))
        button_area.grid(column=1, row=1)

    def image_threshold_double_calculations(self, parent, val_floor, val_celling):
        try:
            int(val_floor)
            int(val_celling)
        except ValueError:
            print("Wpisana wartosc musi by numerem.")
            return
        if not (0 < int(val_floor) < 255) or not (0 < int(val_celling) < 255):
            print("Wartosc poza zakresem 0-255")
            return
        val_floor = int(val_floor)
        val_celling = int(val_celling)
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_thresholded)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(image_thresholded)

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
                           command=lambda: self.image_posterize_calculations(parent, entry.get()))
        label.pack()
        entry.pack()
        button.pack()

    def image_posterize_calculations(self, parent, value):
        try:
            int(value)
        except ValueError:
            print("Wpisana wartosc musi by numerem.")
            return
        if not (1 < int(value) < 255):
            print("Wartosc poza zakresem 0-255")
            return
        value = int(value)
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(image_posterized)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(image_posterized)

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
                                                                                       entry_1.get(),
                                                                                       entry_2.get(),
                                                                                       entry_3.get(),
                                                                                       entry_4.get()))
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
        try:
            int(from_min)
            int(from_max)
            int(to_min)
            int(to_max)
        except ValueError:
            print("Wpisana wartosc musi by numerem.")
            return
        for value in [from_min, from_max, to_min, to_max]:
            if not 0 < int(value) < 255:
                print("Wartosc poza zakresem 0-255")
                return
        from_min = int(from_min)
        from_max = int(from_max)
        to_min = int(to_min)
        to_max = int(to_max)
        values_count = [0 for i in range(256)]
        for value in parent.loaded_image_data[1]:
            values_count[int(value)] += 1
        for index in range(len(parent.edited_image_data[1])):
            if parent.edited_image_data[1][index] < from_min:
                parent.edited_image_data[1][index] = from_min
            if parent.edited_image_data[1][index] > from_max:
                parent.edited_image_data[1][index] = from_max
            else:
                parent.edited_image_data[1][index] = \
                    (((parent.edited_image_data[1][index] - from_min) * (to_max - to_min)) /
                     (from_max - from_min)) + to_min
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(stretch_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Stretched", parent.pil_image_data.getdata()]
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
        result = cv2.blur(parent.cv2_image, (5, 5), 0, borderType=border)
        im_pil = Image.fromarray(result).getdata()
        return im_pil

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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(smoothing_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Linear smoothing", parent.pil_image_data.getdata()]
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
        result = cv2.GaussianBlur(parent.cv2_image, (3, 3), 0, borderType=border)
        im_pil = Image.fromarray(result).getdata()
        return im_pil

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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])

        picture_label = tk.Label(gauss_smoothing_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Linear smoothing", parent.pil_image_data.getdata()]
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
        result = cv2.Laplacian(parent.cv2_image, ddepth, ksize, borderType=border)
        im_pil = Image.fromarray(result).getdata()
        return im_pil

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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(laplacian_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Laplacian", parent.pil_image_data.getdata()]
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(sobel_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["sobel", parent.pil_image_data.getdata()]
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(canny_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["canny", parent.pil_image_data.getdata()]
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(sharpening_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["sharpening", parent.pil_image_data.getdata()]
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(edge_detection_result_window)
        picture_label.pack()
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])

        parent.histogram_image_data = ["edge_detection", parent.pil_image_data.getdata()]
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
        entry_1.insert(0, "1")
        entry_2.insert(0, "1")
        entry_3.insert(0, "1")
        entry_4.insert(0, "1")
        entry_5.insert(0, "2")
        entry_6.insert(0, "1")
        entry_7.insert(0, "1")
        entry_8.insert(0, "1")
        entry_9.insert(0, "1")

        button_area = tk.Frame(self.linear_neighbour_op_window, width=100, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.linear_neighbour_op_calculations(parent, entry_1.get(),
                                                                                 entry_2.get(),
                                                                                 entry_3.get(),
                                                                                 entry_4.get(),
                                                                                 entry_5.get(),
                                                                                 entry_6.get(),
                                                                                 entry_7.get(),
                                                                                 entry_8.get(),
                                                                                 entry_9.get()))
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
        helper_list = [xy_11, xy_12, xy_13, xy_21, xy_22, xy_23, xy_31, xy_32, xy_33]
        try:
            [int(value) for value in helper_list]
        except ValueError:
            print("Wpisana wartosc musi by numerem.")
            return
        xy_11 = int(xy_11)
        xy_12 = int(xy_12)
        xy_13 = int(xy_13)
        xy_21 = int(xy_21)
        xy_22 = int(xy_22)
        xy_23 = int(xy_23)
        xy_31 = int(xy_31)
        xy_32 = int(xy_32)
        xy_33 = int(xy_33)
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(linear_neighbour_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Neightbour_op", parent.pil_image_data.getdata()]
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
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(median_filter_result_window)
        picture_label.pack()
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])

        parent.histogram_image_data = ["median_filter", parent.pil_image_data.getdata()]
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
        second_arg = numpy.array(parent.all_open_image_data[img_two])
        second_cv2 = cv2.resize(second_arg, (first_cv2.shape[1], first_cv2.shape[0]))
        add_result = cv2.add(first_cv2, second_cv2)
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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])

        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_add_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["Added", parent.pil_image_data.getdata()]
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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_subtract_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["subtracted", parent.pil_image_data.getdata()]
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
        try:
            int(weight_one)
            int(weight_two)
            int(gamma_val)
        except ValueError:
            print("Wpisana wartosc musi by numerem.")
            return
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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_blend_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["blended", parent.pil_image_data.getdata()]
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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_and_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["and", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_and_result_window.mainloop()

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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_or_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["or", parent.pil_image_data.getdata()]
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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_not_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["not", parent.pil_image_data.getdata()]
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
        parent.save_helper_image_data = Image.new(parent.all_open_image_data[img_one].mode,
                                                  parent.all_open_image_data[img_one].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        picture_label = tk.Label(math_xor_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["xor", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        math_xor_result_window.mainloop()


class MenuBarLab4(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)
        self.border_pixel_methods = {"Izolacja": cv2.BORDER_ISOLATED,
                                     "Odbicie": cv2.BORDER_REFLECT,
                                     "Replikacja": cv2.BORDER_REPLICATE}
        self.morph_shapes = {"Romb": numpy.uint8(numpy.add.outer(*[numpy.r_[:1, 1:-1:-1]] * 2) >= 1),
                             "Kwadrat": cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))}
        self.operation_Type = {"Erozja": 0,
                               "Dylacja": 1,
                               "Otwarcie": 2,
                               "Zamknięcie": 3}
        self.filtration_type = {"Dwuetapowa z użyciem dwóch masek 3x3": 0,
                                "Jednoetapowa z użyciem maski 5x5": 1}

    def morph_ops(self, parent):
        self.morph_ops_window = tk.Toplevel(parent)
        self.morph_ops_window.resizable(False, False)
        self.morph_ops_window.title("Ustawienia")
        self.morph_ops_window.focus_set()

        image_erode_settings_top = tk.Frame(self.morph_ops_window, width=150, height=150)
        label_0 = tk.Label(image_erode_settings_top, text="Operacja", padx=10)
        combobox_0 = ttk.Combobox(image_erode_settings_top, state='readonly', width=45)
        combobox_0["values"] = list(self.operation_Type.keys())
        combobox_0.current(0)

        label_1 = tk.Label(image_erode_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_1 = ttk.Combobox(image_erode_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.border_pixel_methods.keys())
        combobox_1.current(0)

        label_2 = tk.Label(image_erode_settings_top, text="Element strukturalny", padx=10)
        combobox_2 = ttk.Combobox(image_erode_settings_top, state='readonly', width=45)
        combobox_2["values"] = list(self.morph_shapes.keys())
        combobox_2.current(0)

        button_area = tk.Frame(self.morph_ops_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.morph_ops_controler(
                               parent,
                               self.operation_Type[combobox_0.get()],
                               self.border_pixel_methods[combobox_1.get()],
                               self.morph_shapes[combobox_2.get()]))
        button.pack()

        image_erode_settings_top.grid(column=0, row=0)
        label_0.grid(column=0, row=0, padx=(25, 5))
        combobox_0.grid(column=0, row=1, padx=(20, 5))
        label_1.grid(column=0, row=2, padx=(25, 5))
        combobox_1.grid(column=0, row=3, padx=(20, 5))
        label_2.grid(column=0, row=4, padx=(25, 5))
        combobox_2.grid(column=0, row=5, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def morph_ops_controler(self, parent, operation_index, border_pixel_method, morph_shape):
        parent.edited_image_data[1] = self.morph_ops_calculations(parent, operation_index,
                                                                  border_pixel_method, morph_shape)
        self.morph_ops_result_window(parent)

    def morph_ops_calculations(self, parent, operation_index, border_pixel_method, morph_shape):
        erode_img = self.morph_ops_method(parent, operation_index, border_pixel_method, morph_shape)
        im_pil = Image.fromarray(erode_img).getdata()
        return im_pil

    def morph_ops_method(self, parent, operation_index, border_pixel_method, morph_shape):
        if operation_index == 0:
            return cv2.erode(parent.cv2_image, morph_shape, iterations=2, borderType=border_pixel_method)
        elif operation_index == 1:
            return cv2.dilate(parent.cv2_image, morph_shape, iterations=2, borderType=border_pixel_method)
        elif operation_index == 2:
            return cv2.morphologyEx(parent.cv2_image, cv2.MORPH_OPEN, morph_shape,
                                    borderType=border_pixel_method)
        elif operation_index == 3:
            return cv2.morphologyEx(parent.cv2_image, cv2.MORPH_CLOSE, morph_shape,
                                    borderType=border_pixel_method)

    def morph_ops_result_window(self, parent):
        self.morph_ops_window.destroy()
        erode_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - operacja morfologiczna"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - operacja morfologiczna({str(helper_index)})"
        erode_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            erode_result_window.destroy()

        erode_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1])
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1])
        picture_label = tk.Label(erode_result_window)
        picture_label.pack()
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(list(parent.edited_image_data[1]))

        parent.histogram_image_data = ["morphological operation", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        erode_result_window.mainloop()

    def filter_ops(self, parent):
        self.filter_ops_window = tk.Toplevel(parent)
        self.filter_ops_window.resizable(False, False)
        self.filter_ops_window.title("Ustawienia")
        self.filter_ops_window.focus_set()

        image_erode_settings_top = tk.Frame(self.filter_ops_window, width=150, height=150)

        label_0 = tk.Label(image_erode_settings_top, text="Ustawienia pikseli brzegowych", padx=10)
        combobox_0 = ttk.Combobox(image_erode_settings_top, state='readonly', width=45)
        combobox_0["values"] = list(self.border_pixel_methods.keys())
        combobox_0.current(0)
        label_1 = tk.Label(image_erode_settings_top, text="Rodzaj filtracji", padx=10)
        combobox_1 = ttk.Combobox(image_erode_settings_top, state='readonly', width=45)
        combobox_1["values"] = list(self.filtration_type.keys())
        combobox_1.current(0)
        button_area = tk.Frame(self.filter_ops_window, width=50, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.filter_ops_controler(
                               parent,
                               self.border_pixel_methods[combobox_0.get()],
                               self.filtration_type[combobox_1.get()]))
        button.pack()

        image_erode_settings_top.grid(column=0, row=0)
        label_0.grid(column=0, row=0, padx=(25, 5))
        combobox_0.grid(column=0, row=1, padx=(20, 5))
        label_1.grid(column=0, row=2, padx=(25, 5))
        combobox_1.grid(column=0, row=3, padx=(20, 5))
        button_area.grid(column=0, row=1, padx=(20, 5))

    def filter_ops_controler(self, parent, border_pixel_method, filter_type):
        parent.edited_image_data[1] = self.filter_ops_calculations(parent, border_pixel_method, filter_type)
        self.filter_ops_result_window(parent)

    def filter_ops_calculations(self, parent, border_pixel_method, filter_type):
        mf = numpy.ones((3, 3))
        mg = numpy.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]])

        mh = conv2(mf, mg, mode='full')
        if filter_type == 0:
            res_step1 = cv2.filter2D(parent.cv2_image, cv2.CV_64F, mf, borderType=border_pixel_method)
            result = cv2.filter2D(res_step1, cv2.CV_64F, mg, borderType=border_pixel_method)
        elif filter_type == 1:
            result = cv2.filter2D(numpy.array(parent.loaded_image_data[2]), cv2.CV_64F, mh,
                                  borderType=border_pixel_method)
        im_pil = Image.fromarray(result)
        return im_pil

    def filter_ops_result_window(self, parent):
        self.filter_ops_window.destroy()
        erode_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - operacja filtracji"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - operacja filtracji({str(helper_index)})"
        erode_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            erode_result_window.destroy()

        erode_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1].getdata())
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1].getdata())
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1].getdata())
        picture_label = tk.Label(erode_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["filter operation", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        erode_result_window.mainloop()

    def skeletonize_img(self, parent):
        if parent.loaded_image_type != 'b':
            print("Obraz musi byc binarny")
            return
        self.skeletonize_img_controler(parent)

    def skeletonize_img_controler(self, parent):
        parent.edited_image_data[1] = self.skeletonize_img_calculations(parent)
        self.skeletonize_img_result_window(parent)

    def skeletonize_img_calculations(self, parent):
        helper = numpy.array(parent.loaded_image_data[2])
        skel = numpy.zeros(helper.shape, numpy.uint8)
        im_copy = helper.copy()
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        while True:
            im_open = cv2.morphologyEx(im_copy, cv2.MORPH_OPEN, element)
            im_temp = cv2.subtract(im_copy, im_open)
            im_eroded = cv2.erode(im_copy, element)
            skel = cv2.bitwise_or(skel, im_temp)
            im_copy = im_eroded.copy()

            if cv2.countNonZero(im_copy) == 0:
                break

        im_pil = Image.fromarray(skel)
        return im_pil

    def skeletonize_img_result_window(self, parent):
        erode_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - operacja filtracji"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - operacja filtracji({str(helper_index)})"
        erode_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            erode_result_window.destroy()

        erode_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1].getdata())
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1].getdata())
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1].getdata())
        picture_label = tk.Label(erode_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["filter operation", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        erode_result_window.mainloop()


class MenuBarLab5(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)
        self.threshold_calc_method = {"Na podstawie wartości średniej": cv2.ADAPTIVE_THRESH_MEAN_C,
                                      "Na podstawie średniej ważonej": cv2.ADAPTIVE_THRESH_GAUSSIAN_C}
        self.threshold_method = {"Zwykłe": cv2.THRESH_BINARY,
                                 "Z inwersją": cv2.THRESH_BINARY_INV}

    def image_threshold(self, parent):
        self.menu_stretch_settings_window = tk.Toplevel(parent)
        self.menu_stretch_settings_window.title("Ustawienia progowania")
        self.menu_stretch_settings_window.resizable(False, False)
        self.menu_stretch_settings_window.geometry("350x80")
        self.menu_stretch_settings_window.focus_set()

        label = tk.Label(self.menu_stretch_settings_window, text="Próg", justify=tk.LEFT, anchor='w')

        self.scale_widget = tk.Scale(self.menu_stretch_settings_window, from_=1, to=255,
                                     orient=tk.HORIZONTAL, length=320,
                                     command=lambda arg=None: self.image_threshold_calc_refresh(parent,
                                                                                                int(self.scale_widget.get())))

        self.old_value = self.scale_widget.get()

        button = tk.Button(self.menu_stretch_settings_window, text="Zamknij", width=10,
                           command=lambda: self.menu_stretch_settings_window.destroy())

        self.threshold_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - progowanie interakcyjne"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - progowanie interakcyjne({str(helper_index)})"
        self.threshold_result_window.title('Obraz wynikowy - progowanie ręczne')
        self.picture_label = tk.Label(self.threshold_result_window)
        self.picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.loaded_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.loaded_image_data[1])

        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        self.picture_label.configure(image=selected_picture)

        self.scale_widget.pack()

        button.pack()
        self.threshold_result_window.mainloop()

    def image_threshold_calc_refresh(self, parent, new_value):
        """
        Refreshes and calculates displayed image every time scale widget is moved.
        :param parent:
        :param new_value:
        :return:
        """
        for s in range(5):  # continue only if after 0.5s selected threshold value is not changed
            sleep(0.1)
            if self.scale_widget.get() != new_value:
                return

        # calculate thresholded img
        new_picture = self.image_threshold_calculations(parent, new_value)
        # update image in image window
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(new_picture)

        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(new_picture)
        parent.all_open_image_data["Obraz wynikowy - progowanie ręczne"] = parent.pil_image_data
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)

        self.picture_label.configure(image=selected_picture)
        self.picture_label.image = selected_picture

    def image_threshold_calculations(self, parent, value):
        image_thresholded = list(parent.loaded_image_data[1])
        for index in range(len(parent.loaded_image_data[1])):
            if parent.loaded_image_data[1][index] > value:
                image_thresholded[index] = 255
            else:
                image_thresholded[index] = 0
        return image_thresholded

    def image_threshold_adaptive(self, parent):
        self.menu_stretch_settings_window = tk.Toplevel(parent)
        self.menu_stretch_settings_window.title("Ustawienia progowania")
        self.menu_stretch_settings_window.resizable(False, False)
        self.menu_stretch_settings_window.geometry("350x200")
        self.menu_stretch_settings_window.focus_set()

        label_1 = tk.Label(self.menu_stretch_settings_window, text="Sposób liczenia progu", padx=10)
        combobox_1 = ttk.Combobox(self.menu_stretch_settings_window, state='readonly', width=45)
        combobox_1["values"] = list(self.threshold_calc_method.keys())
        combobox_1.current(0)

        label_2 = tk.Label(self.menu_stretch_settings_window, text="Sposób progowania", padx=10)
        combobox_2 = ttk.Combobox(self.menu_stretch_settings_window, state='readonly', width=45)
        combobox_2["values"] = list(self.threshold_method.keys())
        combobox_2.current(0)

        label_3 = tk.Label(self.menu_stretch_settings_window, text="Próg", justify=tk.LEFT, anchor='w')
        self.scale_widget = tk.Scale(self.menu_stretch_settings_window, from_=1, to=255,
                                     orient=tk.HORIZONTAL, length=320,
                                     command=lambda scale_value: self.image_threshold_adaptive_calc_refresh(parent,
                                                                                                            self.threshold_calc_method[
                                                                                                                combobox_1.get()],
                                                                                                            self.threshold_method[
                                                                                                                combobox_2.get()],
                                                                                                            int(scale_value)))

        self.old_value = self.scale_widget.get()

        button = tk.Button(self.menu_stretch_settings_window, text="Zamknij", width=10,
                           command=lambda: self.menu_stretch_settings_window.destroy())
        label_1.pack()
        combobox_1.pack()
        label_2.pack()
        combobox_2.pack()
        label_3.pack()
        self.threshold_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - progowanie interakcyjne"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - progowanie interakcyjne({str(helper_index)})"
        self.threshold_result_window.title('Obraz wynikowy - progowanie ręczne')
        self.picture_label = tk.Label(self.threshold_result_window)
        self.picture_label.pack()
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.loaded_image_data[1])
        parent.all_open_image_data[img_title] = parent.pil_image_data
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.loaded_image_data[1])

        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        self.picture_label.configure(image=selected_picture)
        self.scale_widget.pack()
        button.pack()
        self.threshold_result_window.mainloop()

    def image_threshold_adaptive_calc_refresh(self, parent, adaptive_method, threshold_type, block_size):
        """
        Refreshes and calculates displayed image every time scale widget is moved.
        :param parent:
        :param adaptive_method:
        :param threshold_type:
        :param block_size:
        :return:
        """
        # calculate thresholded img
        if not (block_size % 2) or block_size == 1:
            return
        new_picture = self.image_threshold_adaptive_calculations(parent, adaptive_method, threshold_type, block_size)
        # update image in image window
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(new_picture)

        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(new_picture)
        parent.all_open_image_data["Obraz wynikowy - progowanie ręczne"] = parent.pil_image_data
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)

        self.picture_label.configure(image=selected_picture)
        self.picture_label.image = selected_picture

    def image_threshold_adaptive_calculations(self, parent, adaptive_method, threshold_type, block_size):
        img_th_adapt = cv2.adaptiveThreshold(parent.cv2_image, 255, adaptive_method, threshold_type, block_size, 5)
        result = Image.fromarray(img_th_adapt).getdata()
        return result

    def image_threshold_otsu(self, parent):
        self.menu_stretch_otsu_settings_window = tk.Toplevel(parent)
        self.menu_stretch_otsu_settings_window.title("Ustawienia progowania")
        self.menu_stretch_otsu_settings_window.resizable(False, False)
        self.menu_stretch_otsu_settings_window.geometry("300x120")
        self.menu_stretch_otsu_settings_window.focus_set()

        label = tk.Label(self.menu_stretch_otsu_settings_window, text="Sposób progowania", padx=10)
        combobox = ttk.Combobox(self.menu_stretch_otsu_settings_window, state='readonly', width=45)
        combobox["values"] = list(self.threshold_method.keys())
        combobox.current(0)

        label_1 = tk.Label(self.menu_stretch_otsu_settings_window, text="Najpierw rozmyj", padx=10)
        combobox_1 = ttk.Combobox(self.menu_stretch_otsu_settings_window, state='readonly', width=45)
        combobox_1["values"] = ['Tak', 'Nie']
        combobox_1.current(0)

        button = tk.Button(self.menu_stretch_otsu_settings_window, text="Wykonaj", width=10,
                           command=lambda: self.image_threshold_otsu_calc_controller(parent,
                                                                                     self.threshold_method[
                                                                                         combobox.get()],
                                                                                     combobox_1.get()))
        label.pack()
        combobox.pack()
        label_1.pack()
        combobox_1.pack()
        button.pack()

    def image_threshold_otsu_calc_controller(self, parent, threshold_type, blur_first):
        new_picture = self.image_threshold_otsu_calculations(parent, threshold_type, blur_first)

        self.threshold_otsu_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - progowanie met. Otsu"
        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - progowanie met. Otsu({str(helper_index)})"
        self.threshold_otsu_result_window.title(img_title)
        self.picture_label = tk.Label(self.threshold_otsu_result_window)
        self.picture_label.pack()

        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(new_picture)

        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(new_picture)
        parent.all_open_image_data[img_title] = parent.pil_image_data
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)

        self.picture_label.configure(image=selected_picture)
        self.picture_label.image = selected_picture

    def image_threshold_otsu_calculations(self, parent, threshold_type, blur_first):
        self.menu_stretch_otsu_settings_window.destroy()
        if blur_first == "Tak":
            blur = cv2.GaussianBlur(parent.cv2_image, (5, 5), 0)
            calculate = cv2.threshold(blur, 0, 255, threshold_type + cv2.THRESH_OTSU)
            result = Image.fromarray(calculate[1]).getdata()
        else:
            calculate = cv2.threshold(parent.cv2_image, 0, 255, threshold_type + cv2.THRESH_OTSU)
            result = Image.fromarray(calculate[1]).getdata()
        return result

    def watershed_segmentation(self, parent):
        self.watershed_segmentation_controler(parent)

    def watershed_segmentation_controler(self, parent):
        parent.edited_image_data[1] = self.watershed_segmentation_calculations(parent)
        if parent.edited_image_data[1] is not None:
            self.watershed_segmentation_result_window(parent)

    def watershed_segmentation_calculations(self, parent):
        """
        handles the calculations
        :param parent: reference to outermost window and its parameters
        :return im_pil: image in pil Image format
        """
        if parent.loaded_image_type != 'c':
            print("Do segmentacji musi byc uzyty kolorowy obraz!")
            return None
        image = parent.cv2_image

        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret2, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = numpy.ones((3, 3), numpy.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        sure_bg = cv2.dilate(opening, kernel, iterations=1)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
        sure_fg = numpy.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        markers2 = cv2.watershed(parent.cv2_image, markers)
        img_gray[markers2 == -1] = 255
        image[markers2 == -1] = [255, 0, 0]
        result = cv2.applyColorMap(numpy.uint8(markers2 * 10), cv2.COLORMAP_JET)

        im_pil = Image.fromarray(result)
        return im_pil

    def watershed_segmentation_result_window(self, parent):
        """
        Displays result window
        :param parent: reference to outermost window and its parameters
        """
        erode_result_window = tk.Toplevel()
        img_title = "Obraz wynikowy - segmentacja met. wododziałową"

        helper_index = 0
        while img_title in parent.all_open_image_data.keys():
            helper_index += 1
            img_title = f"Obraz wynikowy - segmentacja met. wododziałową({str(helper_index)})"
        erode_result_window.title(img_title)

        def on_closing():
            del parent.all_open_image_data[img_title]
            erode_result_window.destroy()

        erode_result_window.protocol("WM_DELETE_WINDOW", on_closing)
        parent.all_open_image_data[img_title] = list(parent.edited_image_data[1].getdata())
        parent.pil_image_data = Image.new(parent.loaded_image_mode,
                                          parent.loaded_image_data[2].size)
        parent.pil_image_data.putdata(parent.edited_image_data[1].getdata())
        parent.save_helper_image_data = Image.new(parent.loaded_image_mode,
                                                  parent.loaded_image_data[2].size)
        parent.save_helper_image_data.putdata(parent.edited_image_data[1].getdata())
        picture_label = tk.Label(erode_result_window)
        picture_label.pack()

        parent.histogram_image_data = ["watershed segmentation", parent.pil_image_data.getdata()]
        selected_picture = ImageTk.PhotoImage(parent.pil_image_data)
        picture_label.configure(image=selected_picture)
        erode_result_window.mainloop()


class MenuBarFinal(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def split_image_bits(self, parent):
        """
        Entry point for splitting image into 8 images, each for each bit of input image.
        Opens settings window allowing to change brightness
        :param parent: - reference to outermost window and its parameters
        """
        if parent.loaded_image_type == "c":
            print("Należy załadować szaroodcieniowy.")
            return
        self.split_image_bits_settings_window = tk.Toplevel(parent)

        self.split_image_bits_settings_window.title("Ustawienia")
        self.split_image_bits_settings_window.resizable(False, False)
        self.split_image_bits_settings_window.focus_set()

        top_area = tk.Frame(self.split_image_bits_settings_window, width=300, height=150)
        label = tk.Label(top_area, text="Rozjaśnij obraz. Opcja Nie spowoduje pokazanie obrazów "
                                        "o naturalnych jasnościach bitów", padx=10)
        combobox = ttk.Combobox(top_area, state='readonly', width=45)
        combobox["values"] = ("Tak", "Nie")
        combobox.current(1)
        label.pack()
        combobox.pack()

        select_area = tk.Frame(self.split_image_bits_settings_window, width=300, height=150)
        label_0 = tk.Label(select_area, text="Zaznaczony obszar jest tworzony od górnego lewego rogu, "
                                             "do dolnego prawego rogu wybranego obszaru", padx=10)
        label_0_explanation = tk.Label(select_area, text=f"Szerokość i wysokość obrazu wejściowego: "
                                                         f"{parent.cv2_image.shape[1]}px, "
                                                         f"{parent.cv2_image.shape[0]}px", padx=10)

        label_1 = tk.Label(select_area, text="Od (X,Y)", padx=10)
        entry_1x = tk.Entry(select_area, width=10)
        entry_1y = tk.Entry(select_area, width=10)

        label_2 = tk.Label(select_area, text="Do (X,Y)", padx=10)
        entry_2x = tk.Entry(select_area, width=10)
        entry_2y = tk.Entry(select_area, width=10)

        button_area = tk.Frame(self.split_image_bits_settings_window, width=300, pady=10)
        button = tk.Button(button_area, text="Wykonaj", width=10,
                           command=lambda: self.split_image_bits_controller(parent, combobox.get(),  entry_1x.get(),
                                                                            entry_1y.get(), entry_2x.get(),
                                                                            entry_2y.get()))
        entry_1x.insert(0, "0")
        entry_1y.insert(0, "0")
        entry_2x.insert(0, str(parent.cv2_image.shape[1]))
        entry_2y.insert(0, str(parent.cv2_image.shape[0]))

        label_0.grid(column=0, row=0, columnspan=4)
        label_0_explanation.grid(column=0, row=1, columnspan=4)
        label_1.grid(column=0, row=2, columnspan=2)
        label_2.grid(column=2, row=2, columnspan=2)
        entry_1x.grid(column=0, row=3)
        entry_1y.grid(column=1, row=3)
        entry_2x.grid(column=2, row=3)
        entry_2y.grid(column=3, row=3)

        top_area.grid(column=0, row=0, columnspan=4, rowspan=2)
        select_area.grid(column=0, row=2, columnspan=4, rowspan=2)
        button_area.grid(column=1, row=4, columnspan=2)

        button.pack()

    def split_image_bits_controller(self, parent, brightness, from_x, from_y, to_x, to_y):
        """
        Initiates and controls input and output of calculations, then passess it to split_image_bits_result_windows
        method, to create output windows.
        :param parent: reference to outermost window and its parameters
        :param brightness: Brightness of output image from 0 to 255. If -1 is used, initial brightness of specific bits
        will be used, meaning that in least important bit image, it will be almost impossible to see anything
        other than black colour.
        """
        print("DANE:", from_x, from_y, to_x, to_y)
        try:
            from_x = int(from_x)
            from_y = int(from_y)  # Reverse from_x and from_y due to cv2 image operation taking y coordinate before x
            to_x = int(to_x)
            to_y = int(to_y)
        except ValueError:
            print("Wpisana wartosc musi być numerem.")
            return
        if (from_x > to_x) or (from_y > to_y):
            print("Wartosci punktu poczatkowego wieksze niz wartosc punktu koncowego")
            return
        requirements = ((0 <= from_x < parent.cv2_image.shape[0]), (0 <= from_y < parent.cv2_image.shape[1]),
                        (0 < to_x <= parent.cv2_image.shape[1]), (0 < to_y <= parent.cv2_image.shape[0]))
        if not all(requirements):
            print("Wartosć jednej ze współrzędnych punktu poza możliwym zakresem (0 - rozmiar X lub Y)")
            return

        first_bit_img, second_bit_img, third_bit_img, fourth_bit_img = [], [], [], []
        fifth_bit_img, sixth_bit_img, seventh_bit_img, eighth_bit_img = [], [], [], []

        helper_img = list(Image.fromarray(parent.cv2_image[from_y:to_y, from_x:to_x]).getdata())

        # Create separate 8 images(for each bit) from calculations on input image
        for pixel in helper_img:
            result = self.split_image_bits_calculations(parent, int(pixel), brightness)
            first_bit_img.append(result[0])
            second_bit_img.append(result[1])
            third_bit_img.append(result[2])
            fourth_bit_img.append(result[3])
            fifth_bit_img.append(result[4])
            sixth_bit_img.append(result[5])
            seventh_bit_img.append(result[6])
            eighth_bit_img.append(result[7])

        if brightness == "Tak":
            for i in range(len(first_bit_img)):
                if first_bit_img[i] != 0:
                    first_bit_img[i] = 255
                if second_bit_img[i] != 0:
                    second_bit_img[i] = 255
                if third_bit_img[i] != 0:
                    third_bit_img[i] = 255
                if fourth_bit_img[i] != 0:
                    fourth_bit_img[i] = 255
                if fifth_bit_img[i] != 0:
                    fifth_bit_img[i] = 255
                if sixth_bit_img[i] != 0:
                    sixth_bit_img[i] = 255
                if seventh_bit_img[i] != 0:
                    seventh_bit_img[i] = 255
                if eighth_bit_img[i] != 0:
                    eighth_bit_img[i] = 255

        self.split_image_bits_result_windows(parent, first_bit_img, second_bit_img, third_bit_img, fourth_bit_img,
                                             fifth_bit_img, sixth_bit_img, seventh_bit_img, eighth_bit_img,
                                             from_x, from_y, to_x, to_y)

    def split_image_bits_calculations(self, parent: ApoProjectCore, pixel_int: int, brightness: int):
        """
        Separates and returns specific bits from input image
        :param parent: reference to outermost window and its parameters
        :param pixel_int: Specific pixel in the input image
        :param brightness: Brightness of output image from 0 to 255. If -1 is used, initial brightness of specific bits
        will be used, meaning that in least important bit image, it will be almost impossible to see anything
        other than black colour.
        :return lists_container: dictionary with values from 0 to 7 containing created images.
        """
        template = "________"

        first_bit, second_bit, third_bit, fourth_bit = int("00000000"), int("00000000"), int("00000000"), int(
            "00000000")
        fifth_bit, sixth_bit, seventh_bit, eighth_bit = int("00000000"), int("00000000"), int("00000000"), int(
            "00000000")
        lists_container = {
            0: first_bit,
            1: second_bit,
            2: third_bit,
            3: fourth_bit,
            4: fifth_bit,
            5: sixth_bit,
            6: seventh_bit,
            7: eighth_bit
        }

        editing = str(bin(pixel_int))[2:]  # string without 0b at the start

        # starting range is a workaround coming from binary type variables removing unneccesary zeros,
        # making it shorter than 8 values
        for bit_index in range(8 - len(editing), 8):
            work_template = list(template)
            work_template[bit_index] = editing[bit_index - (8 - len(editing))]
            work_template = [i.replace("_", "0") for i in work_template]
            work_template = "".join(work_template)
            work_template.replace("_", "0")
            lists_container[bit_index] = int(work_template, 2)
        return lists_container

    def split_image_bits_result_windows(self, parent: ApoProjectCore, img_1: list, img_2: list, img_3: list,
                                        img_4: list, img_5: list, img_6: list, img_7: list, img_8: list,
                                        from_x: int, from_y: int, to_x: int, to_y: int):
        """
        Creates 8 windows for image created from each bit.
        :param parent: reference to outermost window and its parameters
        :param img_1: List containing data for greyscale image for most significant bit
        :param img_2: List containing data for greyscale image for specific bit
        :param img_3: List containing data for greyscale image for specific bit
        :param img_4: List containing data for greyscale image for specific bit
        :param img_5: List containing data for greyscale image for specific bit
        :param img_6: List containing data for greyscale image for specific bit
        :param img_7: List containing data for greyscale image for specific bit
        :param img_8: List containing data for greyscale image for least significant bit
        :param from_x: X coordinate of starting point image slicing, when top left corner of image is (0, 0)
        :param from_y: Y coordinate of starting point image slicing, when top left corner of image is (0, 0)
        :param to_x: X coordinate of destination point image slicing, when top left corner of image is (0, 0)
        :param to_y: Y coordinate of destination point image slicing, when top left corner of image is (0, 0)
        """
        size_x = to_x - from_x
        size_y = to_y - from_y
        for i in range(1, 9):
            # Dynamically create windows and name variables for all 8 images, reducing amount of repetitive code by 8x
            exec(f"bit_img_{i} = tk.Toplevel()")
            img_title = "Obraz wynikowy - obraz powstały z konkretnych bitów"
            exec(f"img_title_{i} = 'Obraz wynikowy - obraz powstały z rozdzielenia bitów'")
            while img_title in parent.all_open_image_data.keys():
                exec(f"helper_index_{i} += 1")
                helper_index_helper = f"helper_index_{i}"
                img_title = f"Obraz wynikowy - obraz powstały z {i}-ych bitów(" + exec(helper_index_helper) + ")"
            title_var_name_helper = f"bit_img_{i}"
            exec(f"{title_var_name_helper}.title(\'{img_title} - {i} bit\')")
            exec(f"parent.edited_image_data[1] = img_{i}")

            parent.pil_image_data = Image.new("L",
                                              (size_x, size_y))
            exec(f"parent.pil_image_data.putdata(img_{i})")
            exec(f"picture_label_{i} = tk.Label(bit_img_{i})")
            exec(f"picture_label_{i}.pack()")

            parent.histogram_image_data = ["Image out of specific bit", parent.pil_image_data.getdata()]
            exec(f"self.selected_picture_{i} = ImageTk.PhotoImage(parent.pil_image_data)")
            exec(f"picture_label_{i}.configure(image=self.selected_picture_{i})")


class MenuBarHelp(tk.Menu):
    def __init__(self):
        tk.Menu.__init__(self, tearoff=False)

    def about(self, parent):
        """
        Displays window containing information about application
        """
        about_window = tk.Toplevel(parent)
        about_window.title("O aplikacji")
        about_window.resizable(False, False)
        about_window.focus_set()

        bg_col = "#2C2F33"
        fg_col = "#BBBBBB"
        mainframe = tk.Frame(about_window, padx="70", pady="15", bg=bg_col)
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        tk.Label(mainframe, text="ImageProcessingProject", bg=bg_col, fg=fg_col
                 ).grid(sticky=tk.N, column=1, row=1)
        tk.Label(mainframe, text="Tytuł projektu: Reprezentacja obrazu monochromatycznego w postaci binarnych "
                                 "obrazów każdego bitu oddzielnie  ", bg=bg_col, fg=fg_col
                 ).grid(sticky=tk.N, column=1, row=2)
        tk.Label(mainframe, text="Autor: deelite34", bg=bg_col, fg=fg_col
                 ).grid(column=1, row=3)
        link = tk.Label(mainframe, text="Kod źródłowy: https://github.com/Deelite34/ImageProcessingProject",
                        bg=bg_col, fg="DodgerBlue2", cursor="hand2")
        link.bind("<Button-1>", lambda e: open_new("https://github.com/Deelite34/ImageProcessingProject"))
        link.grid(column=1, row=4)
        tk.Button(mainframe, text="Zamknij", bg=bg_col, fg=fg_col, activebackground=bg_col,
                  activeforeground=fg_col, command=about_window.destroy
                  ).grid(column=1, row=5)