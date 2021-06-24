import cv2
import numpy
from PIL import Image
from PIL import ImageTk
import tkinter as tk

from operations import *


class ApoProjectCore(tk.Tk):
    """
    Outermost class of the project
    Controls main window, initialises adding commands to menubar elements
    Calls another classess as needed.
    Reference to this class is passed as "parent" argument in other methods
    """

    def __init__(self, *args, **kwargs):
        # Gets parent class information, allowing ApoProjectCore to be main window of program
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Projekt")
        self.geometry("700x100")  # Size of main window

        self.menu_bar = MenuBarAdd(self)
        self.config(menu=self.menu_bar)  # Adds menu bar to the main window

        self.resize_width = 500
        self.resize_height = 500
        self.loaded_image_type = None  # Can be b, gs, gs3ch, c; binary, greyscale, greyscale 3 channels, colour
        self.loaded_image_mode = None  # Can be RGB for colour images or L for greyscale

        self.loaded_image_data = []  # Original image(from load_image method) [path, editable_tada, tuple(PIL_DATA)]
        self.edited_image_data = []  # Edited image [path, editable_data, list(PIL_DATA)]
        self.save_helper_image_data = []  # This data is used to save output image to file
        self.cv2_image = None  # image as cv2 object, required for some operations
        self.histogram_image_data = None  # Data used for creating histograms

        self.pil_image_data = None  # Image data in Image format
        self.all_open_image_data = {}  # keys: names of open windows, value: image objects.
        # Helps with handling multiple open windows related operations

    def donothing(self):
        print("ApoProjectCore class donothing() debug func")


class MenuBarAdd(tk.Menu):
    """
    Createa and sets up everything related to menu bar
    """

    def __init__(self, parent: ApoProjectCore):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.file_menu = tk.Menu(self, tearoff=0)
        self.lab_menu_1 = tk.Menu(self, tearoff=0)
        self.lab_menu_2 = tk.Menu(self, tearoff=0)
        self.lab_menu_3 = tk.Menu(self, tearoff=0)
        self.lab_menu_3_math_cascade = tk.Menu(self.lab_menu_3, tearoff=0)
        self.lab_menu_4 = tk.Menu(self, tearoff=0)
        self.lab_menu_4_morph_ops_cascade = tk.Menu(self.lab_menu_4, tearoff=0)
        self.lab_menu_5 = tk.Menu(self, tearoff=0)
        self.lab_menu_final = tk.Menu(self, tearoff=0)
        self.helpmenu = tk.Menu(self, tearoff=0)
        self.menu_bar_fill(parent)

        # Objects for all operations classes
        self.menu_bar_help = MenuBarHelp()
        self.menu_bar_file = MenuBarFile()
        self.menu_bar_lab1 = MenuBarLab1()
        self.menu_bar_lab2 = MenuBarLab2()
        self.menu_bar_lab3 = MenuBarLab3()
        self.menu_bar_lab4 = MenuBarLab4()
        self.menu_bar_lab5 = MenuBarLab5()
        self.menu_bar_final = MenuBarFinal()

    def menu_bar_fill(self, parent: ApoProjectCore):
        """
        Handles adding elements executing specific functions, to the top menu, and submenus
        :param parent: reference to outermost window and its parameters
        """
        self.add_cascade(label="Plik", menu=self.file_menu)
        self.file_menu.add_command(label="Otwórz", command=lambda: self.menu_bar_file.load_image(parent))
        self.file_menu.add_command(label="Zapisz", command=lambda: self.menu_bar_file.save_image(parent))

        self.add_cascade(label="Labolatorium 1", menu=self.lab_menu_1)
        self.lab_menu_1.add_command(label="Histogram", command=lambda: self.menu_bar_lab1.create_histogram(parent),
                                    state=tk.DISABLED)
        self.lab_menu_1.add_command(label="Wypisz otwarte obrazy",
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
        self.lab_menu_3.add_cascade(label="Operacje matematyczne", menu=self.lab_menu_3_math_cascade, state=tk.DISABLED)
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
        self.lab_menu_4.add_command(label="Operacje morfologiczne", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab4.morph_ops(parent))
        self.lab_menu_4.add_command(label="Filtracja jedno lub dwu -etapowa", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab4.filter_ops(parent))
        self.lab_menu_4.add_command(label="Szkieletyzacja", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab4.skeletonize_img(parent))

        self.add_cascade(label="Labolatorium 5", menu=self.lab_menu_5)
        self.lab_menu_5.add_command(label="Progowanie", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab5.image_threshold(parent))
        self.lab_menu_5.add_command(label="Progowanie adaptywne", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab5.image_threshold_adaptive(parent))
        self.lab_menu_5.add_command(label="Progowanie Otsu", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab5.image_threshold_otsu(parent))
        self.lab_menu_5.add_command(label="Segmentacja metodą wododziałową", state=tk.DISABLED,
                                    command=lambda: self.menu_bar_lab5.watershed_segmentation(parent))

        self.add_cascade(label="Zadanie końcowe", menu=self.lab_menu_final)
        self.lab_menu_final.add_command(label="Reprezentacja obrazu monochromatycznego w postaci 8 binarnych obrazów",
                                        state=tk.DISABLED,
                                        command=lambda: self.menu_bar_final.split_image_bits(parent))

        self.add_cascade(label="O programie", menu=self.helpmenu)
        self.helpmenu.add_command(label="Informacja o programie", command=lambda: self.menu_bar_help.about(parent))


if __name__ == "__main__":
    app = ApoProjectCore()
    app.mainloop()
